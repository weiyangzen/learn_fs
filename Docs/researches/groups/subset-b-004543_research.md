# subset-b-004543 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c

## Purpose

This file implements shared e-switch offload termination tables for cases where an FDB rule cannot express all actions directly at its original flow level. It creates a one-entry unmanaged FDB flow table that performs the terminating action list, then rewrites the original destination to forward into that table. The main callers are TC/e-switch offload paths that need RX VLAN push on devices without native support or hairpin-to-uplink termination behavior.

## Important APIs, types, and functions

- `struct mlx5_termtbl_handle` is the cache object stored in `esw->offloads.termtbl_tbl`. It owns the termination flow table, the single rule inside it, copied `flow_act`/vport destination identity, a hash node, and a manual `ref_count`.
- `mlx5_eswitch_termtbl_hash()` and `mlx5_eswitch_termtbl_cmp()` define cache identity from action bits, VLAN push state, destination vport/vhca, and optional packet reformat content.
- `mlx5_eswitch_termtbl_create()` allocates a `MLX5_FLOW_TABLE_TERMINATION | MLX5_FLOW_TABLE_UNMANAGED | MLX5_FLOW_TABLE_TUNNEL_EN_REFORMAT` table in the FDB namespace and installs one forwarding rule.
- `mlx5_eswitch_termtbl_get_create()` serializes cache lookup/creation under `termtbl_mutex`; `mlx5_eswitch_termtbl_put()` decrements the handle and destroys the table/rule when the last user leaves.
- `mlx5_eswitch_termtbl_required()` is the policy gate. It requires termination-table and ignore-flow-level FDB capabilities, excludes skip actions, requires uplink/internal-port source, and returns true for unsupported VLAN-push-on-RX or hairpin-to-uplink patterns.
- `mlx5_eswitch_add_termtbl_rule()` mutates destinations from vport to flow-table destinations and installs the original FTE with `FLOW_ACT_IGNORE_FLOW_LEVEL`.

## Control flow

The caller first checks `mlx5_eswitch_termtbl_required()`. If true, `mlx5_eswitch_add_termtbl_rule()` moves VLAN push actions from the original `flow_act` into a local terminating action, handles per-destination encapsulation reformat, and gets or creates one termination table per unique action/destination tuple. It then changes each vport destination to `MLX5_FLOW_DESTINATION_TYPE_FLOW_TABLE` and adds the actual FDB rule. On any failure, it reverses the action move, restores destination vport metadata, drops acquired termination-table references, and falls back to adding the original rule directly.

## State and persistence

All persistent state is runtime kernel state and firmware flow-steering state. The hash table stores live termination table handles keyed by action/destination identity. Each handle owns firmware flow table and rule objects until `ref_count` reaches zero. No on-disk state exists. The code mutates caller-owned `flow_act`, `dest`, and `attr->dests[*].termtbl` during setup, so rollback correctness matters.

## Dependencies and integration points

This file depends on mlx5 flow steering (`mlx5_create_auto_grouped_flow_table`, `mlx5_add_flow_rules`, `mlx5_destroy_flow_table`), e-switch offload metadata (`struct mlx5_eswitch`, `struct mlx5_esw_flow_attr`), TC flags, and FDB capabilities from device firmware. It integrates with rule deletion through `mlx5_eswitch_termtbl_put()` calls by the owning e-switch/TC cleanup path.

## Risks

Cache key correctness is critical: missing a field can cause rules with different VLAN/reformat/vport semantics to share a termination table. The hash uses `sizeof(dest->vport.num)` when hashing `vhca_id`, which should be reviewed if the field widths differ. Fallback after partial mutation must keep `attr->dests` and `dest[]` aligned. Concurrent lifetime is protected by `termtbl_mutex`, but destruction occurs after unlock, so callers must not use a handle after put.

## Test signals

Useful signals include TC offload tests for VLAN push on RX, hairpin-to-uplink, encapsulated vport destinations, multi-destination rollback, and shared-rule deletion. Hardware tests should cover devices with and without `VLAN_PUSH_ON_RX`, `termination_table`, and `ignore_flow_level` capabilities. Leak checks should verify firmware table/rule objects are destroyed when the last referencing flow is removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/eswitch_offloads_termtbl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/events.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/events.c

## Purpose

This file owns the general mlx5 core event dispatcher. It registers low-level EQ notifiers for firmware events, handles a small set of core diagnostics locally, forwards selected firmware events to mlx5 consumers, and provides a separate blocking notifier chain for driver-generated software events.

## Important APIs, types, and functions

- `struct mlx5_events` is attached at `dev->priv.events`. It owns the workqueue, registered EQ notifier wrappers, firmware atomic notifier chain, software blocking notifier chain, port-module statistics, and PCIe power work item.
- `events_nbs_ref[]` is the registration template for core handlers and forwarded event classes.
- `any_notifier()` logs all events at debug level; `temp_warn()` emits rate-limited high-temperature warnings and optional hwmon sensor names; `port_module()` updates port-module status/error counters and logs cable/module state; `pcie_core()` queues PCI power-status work for general PCI power-change events.
- `forward_event()` calls `atomic_notifier_call_chain(&events->fw_nh, event, data)` for mlx5e/mlx5_ib and other consumers.
- Public entry points include `mlx5_events_init/cleanup/start/stop`, `mlx5_notifier_register/unregister/call_chain`, `mlx5_blocking_notifier_register/unregister/call_chain`, and `mlx5_get_pme_stats()`.

## Control flow

Initialization allocates `struct mlx5_events`, initializes notifier heads, creates a single-thread workqueue, and stores it in `dev->priv.events`. Start copies each template notifier, stores the events context, and registers it with the EQ layer. Event callbacks either log/update local state or forward to consumer chains. Stop unregisters in reverse order and flushes the workqueue so queued PCIe work finishes before cleanup. Cleanup destroys the workqueue and frees the events object.

## State and persistence

Persistent runtime state is limited to notifier registration, `pme_stats`, and queued PCIe work. `pme_stats.status_counters[]` and `error_counters[]` accumulate until device cleanup. There is no disk persistence. PCIe power work reads `MLX5_REG_MPEIN` only when `pci_status_and_power` is supported.

## Dependencies and integration points

The file depends on `lib/eq.h` notifier registration, Linux notifier chains, optional `CONFIG_HWMON`, mlx5 register access, and device capability macros. It is the public event registration surface for mlx5 Ethernet and RDMA consumers. FPGA-specific, e-switch-specific, clock, tracer, and other feature events are intentionally handled elsewhere.

## Risks

Event ordering depends on start/stop registration order. Forwarded `GENERAL_EVENT` also has a local `pcie_core` handler, so consumers must tolerate seeing the same firmware event class through the atomic chain. `mlx5_get_pme_stats()` returns a non-atomic structure copy without explicit locking; counters are simple diagnostics. Workqueue creation failure must leave `dev->priv.events` either unused or cleaned by caller paths.

## Test signals

Tests should exercise event registration/unregistration during device start/stop, module plug/unplug/error EQEs, temperature warning EQEs with and without hwmon, PCI power-change general events, and consumer notifier delivery. Race tests should include unregister while events are in flight and cleanup after queued PCIe work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.c

## Purpose

This file is the low-level command/register bridge for mlx5 Innova FPGA support. It encodes FPGA access, capability, control, query, FPGA QP, and FPGA QP counter commands into mlx5 firmware command/register layouts.

## Important APIs, types, and functions

- `mlx5_fpga_access_reg()` validates 4-byte alignment and maximum transfer size, then reads or writes `MLX5_REG_FPGA_ACCESS_REG`.
- `mlx5_fpga_caps()` reads `MLX5_REG_FPGA_CAP` into `dev->caps.fpga`.
- `mlx5_fpga_ctrl_op()` writes a control operation into `MLX5_REG_FPGA_CTRL`.
- `mlx5_fpga_sbu_caps()` reads the sandbox extended capability blob in chunks using `mlx5_fpga_access_reg()`.
- `mlx5_fpga_query()` reads status and selected admin/operational image from `MLX5_REG_FPGA_CTRL`.
- `mlx5_fpga_create_qp()`, `modify_qp()`, `query_qp()`, `destroy_qp()`, and `query_qp_counters()` wrap FPGA-specific firmware opcodes and copy QPC/counter fields to/from callers.

## Control flow

Most functions build a stack `in` buffer with `MLX5_SET` macros, call `mlx5_core_access_reg()` or `mlx5_cmd_exec*()`, then decode output fields. `mlx5_fpga_sbu_caps()` loops over the device-advertised capability length and advances the FPGA address and caller buffer pointer by each successful read.

## State and persistence

No state is stored in this file except the side effect of updating `dev->caps.fpga`. Firmware state affected by these calls includes FPGA control operation state, sandbox capability reads, and FPGA-owned QP objects/counters. Query-counter can optionally clear counters through the command `clear` bit.

## Dependencies and integration points

The code depends on generated mlx5 IFC layouts, command opcodes, `mlx5_core_access_reg()`, and `mlx5_cmd_exec*()`. It is consumed by `fpga/core.c` for startup/status/control, `fpga/conn.c` for remote FPGA QP lifecycle, and `fpga/sdk.c` for memory/capability API calls.

## Risks

Alignment and size validation protects the FPGA access register, but callers must still chunk unaligned logical operations themselves. `mlx5_fpga_sbu_caps()` uses a `void *` pointer increment, which relies on GNU C semantics used in the kernel. Buffer size must match `sandbox_extended_caps_len` or the function fails. QPC copies use fixed firmware field sizes, so layout drift would corrupt QP creation/modification.

## Test signals

Validation should cover aligned and unaligned FPGA access reads/writes, SBU capability reads larger than one register window, FPGA status query for success/failure/in-progress, QP create/modify/query/destroy, and counter query with and without clear. Fault injection on command failures should verify no caller-visible partial QP identity is trusted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.h

## Purpose

This header declares the internal FPGA command ABI used by the mlx5 FPGA core and connection layers. It defines device/image/status enums, the query result structure, QP modify field selection, QP counter structure, and command helper prototypes.

## Important APIs, types, and functions

- `enum mlx5_fpga_id` names supported Innova FPGA card families: Newton, Edison, Morse, and MorseQ.
- `enum mlx5_fpga_image` distinguishes user and factory images.
- `enum mlx5_fpga_status` mirrors firmware load/control status values, including `SUCCESS`, `FAILURE`, `IN_PROGRESS`, and `NONE`.
- `struct mlx5_fpga_query` carries admin image, operational image, and status returned by `mlx5_fpga_query()`.
- `enum mlx5_fpga_qpc_field_select` currently exposes `MLX5_FPGA_QPC_STATE` for state-only QP modification.
- `struct mlx5_fpga_qp_counters` carries packet/drop counters decoded from firmware.
- Prototypes expose capability, query, control, register access, SBU capability, FPGA QP lifecycle, and FPGA QP counter helpers.

## Control flow

The header has no runtime control flow. It defines the contract that `cmd.c` implements and that `core.c`, `conn.c`, and `sdk.c` consume.

## State and persistence

The header describes firmware-visible state but stores none. The enums and structures must remain aligned with mlx5 firmware encodings because they gate image status interpretation and QP state transitions.

## Dependencies and integration points

It includes `linux/mlx5/driver.h` for mlx5 core types and kernel integer helpers. It is internal to the mlx5 FPGA feature and is included by `fpga/core.h`, `fpga/core.c`, `fpga/conn.c`, and `fpga/sdk.c` through direct or indirect paths.

## Risks

Incorrect enum values would misclassify hardware and image state. Adding QPC field bits without updating command handling could cause firmware modifications to use stale QPC data. The `MLX5_FPGA_STATUS_NONE = 0xFFFF` sentinel is used as software state as well as a status-like value, so consumers must not treat it as a firmware success code.

## Test signals

Build coverage with `CONFIG_MLX5_FPGA` is the main compile-time signal. Runtime tests should verify query status decoding, image name/status handling in `core.c`, and state-only QP modification in `conn.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c

## Purpose

This file implements the transport used by mlx5 FPGA clients to exchange messages with the FPGA sandbox. It creates a host RoCE RC QP and a matching FPGA QP, maps caller buffers for DMA, posts send/receive WQEs, handles CQ completions, and manages per-device connection resources such as RoCE enablement, UAR, PD, and physical-address mkey.

## Important APIs, types, and functions

- `mlx5_fpga_conn_device_init()` enables RoCE, gets a UAR page, allocates a PD, and creates a PA-mode mkey. `mlx5_fpga_conn_device_cleanup()` tears those resources down.
- `mlx5_fpga_conn_create()` allocates a connection, configures a link-local IPv6 SGID from the local MAC, creates CQ/WQ/QP resources, creates the remote FPGA QP, and transitions both endpoints to active/RTS.
- `mlx5_fpga_conn_destroy()` deactivates the QP, synchronizes completions, destroys FPGA and host QPs, destroys the CQ, clears/frees SGID, and frees the connection.
- `mlx5_fpga_conn_send()` maps a two-entry maximum SG buffer, posts it immediately if SQ space is available, or queues it on the SQ backlog.
- CQ handlers `mlx5_fpga_conn_sq_cqe()`, `mlx5_fpga_conn_rq_cqe()`, and `mlx5_fpga_conn_handle_cqe()` unmap DMA, call completion/receive callbacks, drain backlog, and mark the QP inactive on errors.

## Control flow

Device init is per-FPGA and prepares shared connection resources. Connection creation validates `recv_cb`, reserves/sets an SGID, creates and arms a CQ, creates a host QP, fills an FPGA QPC, creates the FPGA QP, activates the FPGA QP, transitions the host QP through RESET, INIT, RTR, and RTS, and pre-posts receive buffers until the RQ is full. Send submission maps the buffer, locks SQ state, posts or backlogs in order, and rings the UAR doorbell. Completion processing is budgeted by `MLX5_FPGA_CQ_BUDGET`; exhausted budget reschedules the tasklet, otherwise the CQ is rearmed.

## State and persistence

Connection state lives in `struct mlx5_fpga_conn`: host and FPGA QPNs/QPC, CQ work queue, tasklet, host QP WQ, SQ/RQ producer/consumer counters, active flag, SGID index, posted buffer arrays, and backlog list. DMA mappings are transient per posted buffer and must be unmapped on completion or teardown. Receive buffers are owned by the connection and reused after callback return. Send buffers remain caller-owned but must not be modified until the completion callback fires.

## Dependencies and integration points

The implementation depends on mlx5 core QP/CQ/WQ helpers, RoCE GID helpers, DMA mapping APIs, generated IFC layouts, `fpga/cmd.c` for remote FPGA QP lifecycle, and `fpga/sdk.c` for exported SBU connection APIs. It is started only for non-lookaside FPGA modes that participate in network processing.

## Risks

The receive-post loop runs until `mlx5_fpga_conn_post_recv_buf()` fails, relying on RQ fullness to return `-EBUSY`; size bugs could produce excessive allocation. Backlog entries are DMA-mapped before queuing and must always be unmapped by flush/error paths. `mlx5_fpga_conn_flush_send_bufs()` walks the backlog but does not delete entries from the list before connection free, which is acceptable only because the connection is being freed and callbacks own buffer lifetime. Completion handlers set `qp.active` without a single global lock, so teardown and CQ/tasklet synchronization are important.

## Test signals

Tests should cover successful create/connect/destroy, SGID allocation failure cleanup, CQ/QP creation failure cleanup, send when SQ is full, backlog drain order, send and receive completion callbacks, receive repost failure, CQ error syndromes, tasklet budget rescheduling, and destroy while sends/receives are outstanding. DMA debug and lockdep are valuable for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.h

## Purpose

This internal header defines the full FPGA connection object and declares the connection/device lifecycle functions implemented by `conn.c`.

## Important APIs, types, and functions

- `struct mlx5_fpga_conn` combines client callback state, remote FPGA QPC/QPN, CQ state, host QP state, SQ/RQ rings, posted buffer arrays, and SQ backlog.
- The CQ substructure owns `mlx5_cqwq`, `mlx5_wq_ctrl`, `mlx5_core_cq`, and tasklet.
- The QP substructure tracks `active`, SGID index, host `mlx5_wq_qp`, QPN, SQ spinlock/producers/consumers/size/buffers/backlog, and RQ producers/consumers/size/buffers.
- Declared functions are `mlx5_fpga_conn_device_init()`, `mlx5_fpga_conn_device_cleanup()`, `mlx5_fpga_conn_create()`, `mlx5_fpga_conn_destroy()`, and `mlx5_fpga_conn_send()`.

## Control flow

The header has no executable control flow, but it documents ownership boundaries: device-level init/cleanup wraps shared resources, create/destroy wraps one connection, and send queues a DMA buffer through that connection.

## State and persistence

All fields are runtime-only. The SQ spinlock protects SQ producer/consumer counters, the posted-SQ buffer array, and backlog ordering. RQ state is manipulated by connection setup and CQ receive completion handling. Client callbacks are stored in the connection and invoked from completion context paths.

## Dependencies and integration points

The header includes mlx5 CQ/QP definitions, `fpga/core.h`, public `fpga/sdk.h` buffer/attribute definitions, and mlx5 work queue helpers. It is used by `conn.c` and by `sdk.c` as the internal implementation layer for public SBU APIs.

## Risks

Because the full struct is visible within the FPGA core, future users could bypass locking/ownership assumptions. The header exposes raw buffer arrays and counters rather than opaque accessors, so changes to posting/completion invariants must be coordinated with all users.

## Test signals

Compile coverage with `CONFIG_MLX5_FPGA` catches structure dependency drift. Runtime signals come from `conn.c`: queue size power-of-two behavior, SQ lock coverage, CQ teardown synchronization, and callback invocation semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.c

## Purpose

This file owns mlx5 FPGA device discovery, startup, shutdown, health integration, and FPGA error event handling. It decides whether an FPGA is present, validates image load status, initializes connection resources for network-processing FPGA images, and tears down the device on FPGA error events.

## Important APIs, types, and functions

- `mlx5_fpga_init()` allocates `struct mlx5_fpga_device` when the general FPGA capability is present and attaches it to `mdev->fpga`.
- `mlx5_fpga_device_start()` reads FPGA capabilities, checks image load state, logs card/image/SBU identity, reserves GIDs, registers FPGA error EQ notifiers, initializes connection resources, and optionally performs sandbox bypass-reset-bypass.
- `mlx5_fpga_device_stop()` reverses startup for non-lookaside devices and turns sandbox bypass back on for user images.
- `mlx5_fpga_cleanup()` calls stop, frees the FPGA object, and clears `mdev->fpga`.
- `mlx5_fpga_event()` decodes FPGA and FPGA-QP error syndromes, changes behavior based on `fdev->state`, and triggers mlx5 health work on active-device errors.

## Control flow

Startup is capability gated. Lookaside FPGA projects skip QP connection setup because they do not participate in network processing. Non-lookaside startup requires a successful image load, nonzero `shell_caps.max_num_qps`, reserved GIDs, error notifier registration, device connection resource init, and optional reset/bypass sequence for user images. Errors unwind registered notifiers and GID reservations. Stop checks the software state under `state_lock`, marks it inactive, applies bypass if needed, cleans connection resources, unregisters notifiers, and unreserves GIDs.

## State and persistence

`struct mlx5_fpga_device` stores software state under `state_lock`, last admin/oper image values, EQ notifier blocks, and shared connection resources. No disk state exists. Firmware state changed by this file includes FPGA control operations and possibly sandbox bypass/reset state. Error events can trigger health recovery by calling `mlx5_trigger_health_work()`.

## Dependencies and integration points

This file depends on the command helpers in `cmd.c`, connection resource helpers in `conn.c`, mlx5 EQ notifier registration, mlx5 health recovery, and core GID reservation APIs. It is conditionally compiled behind `CONFIG_MLX5_FPGA` through `core.h`.

## Risks

State transitions must remain paired with resource ownership. `mlx5_fpga_device_stop()` returns early for lookaside devices and for failed/non-success states; cleanup relies on those branches matching what startup actually allocated. Error events during startup/teardown are rate-limited or health-triggering depending on `state`. `mlx5_fpga_name()` uses a static buffer for unknown IDs, which is fine for logging but not reentrant as a general API.

## Test signals

Tests should cover devices without FPGA capability, lookaside vs non-lookaside IDs, image load failure, zero-QP capability, connection init failure unwind, user-image bypass/reset operations, FPGA and FPGA-QP error EQEs, and stop/cleanup idempotence. Health recovery tests should confirm active FPGA errors trigger device recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.h

## Purpose

This header defines the internal FPGA device object, logging helpers, and public mlx5-core FPGA lifecycle hooks. It also supplies no-op inline stubs when `CONFIG_MLX5_FPGA` is disabled.

## Important APIs, types, and functions

- `struct mlx5_fpga_device` contains the parent mlx5 core device, FPGA error notifier blocks, `state_lock`, current software state, last admin/oper images, and shared connection resources (`pdn`, `mkey`, `uar`).
- Logging macros prefix messages with `FPGA:` and, for debug/warn/error variants, include function, line, and pid.
- Lifecycle prototypes are `mlx5_fpga_init()`, `mlx5_fpga_cleanup()`, `mlx5_fpga_device_start()`, and `mlx5_fpga_device_stop()`.
- The disabled-config branch makes all lifecycle hooks harmless no-ops returning success.

## Control flow

The header has no runtime control flow except its compile-time `CONFIG_MLX5_FPGA` split. That split allows core mlx5 code to call FPGA hooks unconditionally without requiring FPGA support in the build.

## State and persistence

State is runtime-only and centered on `struct mlx5_fpga_device`. The `state_lock` is the synchronization point for state transitions observed by startup, shutdown, and error event handling.

## Dependencies and integration points

The enabled path includes mlx5 EQ/core headers and `fpga/cmd.h`. The struct is consumed by `core.c`, `conn.c`, and `sdk.c`. The no-op stubs integrate with generic mlx5 device init/cleanup paths in configurations without FPGA support.

## Risks

Any fields added to `struct mlx5_fpga_device` must be initialized in `core.c` allocation/start paths and released in cleanup paths. Logging macros dereference `(__adev)->mdev`, so they require a fully initialized FPGA object. Stub behavior must remain semantically acceptable to callers that expect FPGA absence to be non-fatal.

## Test signals

Build both with and without `CONFIG_MLX5_FPGA`. Runtime tests should assert that generic mlx5 init works on devices without FPGA capability and that enabled builds initialize, start, stop, and clean up FPGA state without leaking connection resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.c

## Purpose

This file implements the exported in-kernel Innova FPGA SDK functions. It adapts public SBU connection APIs to the internal connection implementation and exposes FPGA memory read/write plus SBU capability reads through the FPGA access register.

## Important APIs, types, and functions

- `mlx5_fpga_sbu_conn_create()`, `destroy()`, and `sendmsg()` are exported wrappers around `mlx5_fpga_conn_create/destroy/send()` using `MLX5_FPGA_QPC_QP_TYPE_SANDBOX_QP`.
- `mlx5_fpga_mem_read_i2c()` and `mlx5_fpga_mem_write_i2c()` chunk memory operations by `MLX5_FPGA_ACCESS_REG_SIZE_MAX` and call `mlx5_fpga_access_reg()`.
- `mlx5_fpga_mem_read()` and `mlx5_fpga_mem_write()` validate the requested access type and return the requested size on success.
- `mlx5_fpga_get_sbu_caps()` forwards to `mlx5_fpga_sbu_caps()`.

## Control flow

Connection APIs are direct pass-throughs. Memory read/write reject zero length, reject disconnected FPGA objects without `mdev`, then loop until all bytes have been processed or a command error occurs. Only `MLX5_FPGA_ACCESS_TYPE_I2C` is accepted; `DONTCARE` currently aliases the same enum value, so it also selects I2C.

## State and persistence

The SDK functions do not store state. Connection calls create/destroy state in `conn.c`; memory calls read/write FPGA address space through firmware. Successful read/write functions return `size`, not `0`, so callers should treat positive values as byte counts.

## Dependencies and integration points

The file depends on `fpga/core.h`, `fpga/conn.h`, `fpga/sdk.h`, and the command access helpers in `cmd.c`. The `EXPORT_SYMBOL` declarations make this API available to other in-kernel FPGA client drivers.

## Risks

The header comments describe `0` as success for memory read/write, but the implementation returns the byte count. That mismatch can break callers that only test `ret == 0`. Partial progress is not returned on command error; the first error aborts and returns the error code. Access-type expansion must update both the enum and switch statements.

## Test signals

Tests should cover SBU connection creation/send/destruction, zero-length memory operations, disconnected device handling, reads/writes spanning multiple access-register chunks, command failures mid-transfer, and consumer handling of positive success returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.h

## Purpose

This header is the documented in-kernel API for Innova FPGA client drivers. It defines connection attributes, DMA buffer shapes, memory access types, and exported SBU/memory/capability functions.

## Important APIs, types, and functions

- `SBU_QP_QUEUE_SIZE` and `MLX5_FPGA_CMD_TIMEOUT_MSEC` provide queue and timeout constants for clients.
- `enum mlx5_fpga_access_type` currently maps both I2C and DONTCARE to value `0`.
- `struct mlx5_fpga_dma_entry` describes one virtual/DMA address segment.
- `struct mlx5_fpga_dma_buf` contains up to two SG entries, a DMA direction, an SQ backlog list node, and an optional TX completion callback.
- `struct mlx5_fpga_conn_attr` carries TX/RX queue sizes and receive callback context.
- Public APIs create/destroy/send over SBU connections, read/write FPGA memory, and fetch SBU capabilities.

## Control flow

The header has no executable control flow. Its comments define important callback timing: receive callbacks may run before connection create returns, receive buffers are reusable after callback return, and send buffers must remain stable until completion.

## State and persistence

The data structures describe runtime DMA and callback state only. `dma_addr` is private to the implementation after mapping. `list` is owned by the SQ backlog while a send is queued. No state is persisted outside the kernel runtime.

## Dependencies and integration points

It includes Linux type and DMA-direction headers and forward-declares `mlx5_fpga_conn` and `mlx5_fpga_device`. It is consumed by FPGA client drivers and by internal `conn.c`/`sdk.c`.

## Risks

The API contract around buffer lifetime is strict and easy for clients to violate. The comments claim memory read/write return `0` on success, but `sdk.c` returns the byte count. `MLX5_FPGA_ACCESS_TYPE_DONTCARE` is currently identical to I2C, so callers cannot request a different fast path. Receive callbacks may happen during creation, requiring callers to initialize callback context before invoking create.

## Test signals

Consumer tests should validate callback ordering, send completion status, two-entry SG sends, receive buffer reuse assumptions, memory API return-value interpretation, and behavior when queue sizes are small or saturated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fpga/sdk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.c

## Purpose

This file implements the firmware-backed `struct mlx5_flow_cmds` vtable for flow steering. It translates in-memory flow steering objects into mlx5 firmware commands for flow tables, groups, entries, counters, packet reformat contexts, modify-header contexts, match definers, and root table updates. It also provides stub commands for unsupported/software-only table types.

## Important APIs, types, and functions

- `mlx5_flow_cmds` is populated with firmware implementations; `mlx5_flow_cmd_stubs` provides no-op or unsupported behavior.
- Flow table functions create/destroy/modify tables and update roots, including FDB shared-LAG peer propagation.
- Flow group functions create/destroy groups with vport/other-eswitch metadata.
- `mlx5_cmd_set_fte()` is the central FTE encoder: it writes match values, actions, VLAN push fields, packet reformat IDs, modify-header IDs, crypto, ASO flow-meter controls, destination lists, extended destinations, and counters.
- Flow counter APIs allocate/free/query single and bulk counters.
- Packet reformat and modify-header allocators validate capability limits, allocate firmware contexts, and store resource owner/id.
- Match definer helpers create/destroy general objects of type `MATCH_DEFINER`.
- `mlx5_fs_cmd_get_default()` chooses firmware commands for real table types and stubs otherwise.

## Control flow

Creation functions fill command input buffers with device/table metadata and execute firmware commands. On flow table create, the table size is allocated from `fs_ft_pool`; failure returns the size to the pool. FTE create/update share `mlx5_cmd_set_fte()` with different opmods and modify masks. Root update programs `SET_FLOW_TABLE_ROOT`, with special handling for IB underlay QPNs and shared FDB LAG peers. Resource allocation APIs allocate firmware objects and deallocation APIs best-effort destroy them.

## State and persistence

The file mutates firmware state and writes identifiers back into software objects (`ft->id`, `ft->max_fte`, `fg->id`, reformat/modify-header/definer IDs). Flow counter statistics live in firmware until queried or cleared elsewhere. Table-size pool accounting is software state tied to successful create/destroy.

## Dependencies and integration points

It depends on generated IFC command layouts, `mlx5_cmd_exec*`, device capability macros, `fs_core.h` object definitions, `fs_ft_pool`, e-switch/LAG helpers, and packet reformat ID adapters for DR/HWS ownership. `fs_core.c` calls this vtable through each root namespace.

## Risks

Encoding mistakes in `mlx5_cmd_set_fte()` can misprogram forwarding, counters, VLAN, reformat, modify-header, crypto, or ASO behavior. Extended-destination support is capability-sensitive and limited by `log_max_fdb_encap_uplink`. Shared FDB LAG root update must roll back peers and master root on failure. Deallocators ignore command failures, so firmware leaks are possible on persistent command errors. Stub commands make unsupported table types appear software-only; callers must not expect hardware effects.

## Test signals

Tests should cover table create/destroy pool accounting, miss-table modification, root updates with and without underlay QPNs, shared FDB LAG peer rollback, FTE create/update/delete for every destination type, multi-counter limits, extended encapsulated destinations, packet reformat size validation, modify-header action limits per namespace, match definer lifecycle, and silent L2/TX-root commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.h

## Purpose

This header defines the command-provider interface used by `fs_core.c` to operate on flow steering objects. It abstracts firmware-managed, software-managed, and hardware-steering implementations behind `struct mlx5_flow_cmds`.

## Important APIs, types, and functions

- `struct mlx5_flow_cmds` contains callbacks for flow table/group/FTE lifecycle, root updates, packet reformat and modify-header contexts, namespace peer/create/destroy, match definer lifecycle, and capability reporting.
- Flow counter helpers are declared separately: alloc, bulk alloc, free, query, bulk query length, and bulk query.
- Provider selectors `mlx5_fs_cmd_get_default()` and `mlx5_fs_cmd_get_fw_cmds()` return command vtables.
- Misc command helpers set L2 silent mode and TX flow table root.
- `mlx5_fs_cmd_is_fw_term_table()` identifies termination tables by `MLX5_FLOW_TABLE_TERMINATION`.

## Control flow

The header has no runtime control flow. It defines callback signatures and utility declarations used by root namespaces to dispatch operations.

## State and persistence

No state is stored here. The vtable contract governs how `fs_core.c` persists software objects into firmware or alternate steering backends.

## Dependencies and integration points

It includes `fs_core.h` for object and enum definitions. Firmware implementation lives in `fs_cmd.c`; alternate command providers for DR/HWS are selected by `fs_core.c` when namespace mode changes.

## Risks

The callback contract is broad and stateful: implementations must update IDs, honor root/table/vport metadata, and keep software and hardware synchronized. Adding a callback requires all providers and stubs to be updated. The inline termination-table helper only checks a flag, so it assumes flags accurately reflect firmware object semantics.

## Test signals

Build tests should cover all providers. Runtime tests should exercise switching FDB namespace modes, command-provider fallback, termination table detection, and every callback path through `fs_core.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.c

## Purpose

This file is the main mlx5 flow steering object manager. It builds namespace trees for NIC RX/TX, FDB, sniffer, port selection, RDMA, RDMA transport, and per-vport ACL flows; allocates and destroys flow tables/groups/entries/rules; maintains rule sharing and duplicate-match behavior; keeps firmware miss chains/root tables synchronized; and exposes resource helpers for modify headers, packet reformat, match definers, and underlay QPN roots.

## Important APIs, types, and functions

- Static `init_tree_node` topologies describe root namespace layouts and capability requirements.
- Generic tree helpers (`tree_init_node`, `tree_add_node`, `tree_get_node`, `tree_put_node`, `tree_remove_node`) manage refcounted nodes with per-node semaphores.
- Object allocators create flow tables, flow groups, FTEs, rules, and handles; rhashtable/rhltable indexes accelerate group and FTE lookup.
- Public APIs include `mlx5_create_flow_table`, `mlx5_create_auto_grouped_flow_table`, `mlx5_create_flow_group`, `mlx5_add_flow_rules`, `mlx5_del_flow_rules`, `mlx5_destroy_flow_table`, `mlx5_destroy_flow_group`, namespace getters, vport ACL add/remove, `mlx5_fs_core_alloc/init/cleanup/free`, underlay QPN add/remove, modify-header/reformat/definer helpers, namespace peer/mode setters, and `mlx5_fs_get_capabilities`.
- Chain helpers find adjacent flow tables, connect previous priorities to new tables, update root flow tables, and rewrite `FWD_NEXT_*` rules when next tables change.

## Control flow

Allocation initializes flow-counter stats, table-size pools, steering mode, and slab caches. Initialization registers the devlink flow-steering-mode parameter and creates only the root namespaces supported by device capabilities. Flow table creation validates priority/level, creates firmware table through the root command provider, connects previous miss paths and root table if managed, then inserts the table into the tree sorted by level. Rule insertion validates match masks, destinations, and action conflicts; finds matching flow groups/FTEs; appends to existing FTEs when allowed; handles duplicate-match `NO_APPEND` through pending duplicate state; or creates autogroups/FTEs as needed. Deletion removes rule nodes under the FTE lock, updates firmware if destinations remain, or deletes the FTE and releases parent references when empty.

## State and persistence

All state is runtime kernel and firmware state. `struct mlx5_flow_steering` owns root namespace pointers, steering mode, slab caches, FDB sub-namespace arrays, vport ACL xarrays, and RDMA transport root arrays. Root namespaces own command providers, root table pointer, underlay QPN list, and `chain_lock`. Flow tables own group hash tables, autogroup accounting, level/type/vport/flags, and forward-next rule lists. Flow groups own FTE hash tables and IDA index allocation. FTEs own match values, actions/destinations, optional duplicate pending state, and child rule nodes.

## Dependencies and integration points

The file depends on `fs_cmd.h` providers, `fs_ft_pool`, mlx5 capabilities, e-switch total-vport information, devlink parameters, DR/HWS support probes and command providers, Linux xarray/rhashtable/IDA/refcount/rwsem primitives, and tracepoints. It is consumed by mlx5 Ethernet, RDMA, e-switch, TC, IPsec/MACsec, sniffer, and steering-mode management paths.

## Risks

This is a high-concurrency, high-blast-radius file. Refcount/lock ordering bugs can leak nodes, delete live firmware objects, or deadlock; the nested lock classes are important. Firmware chain synchronization must remain correct when first/last tables in a priority are created or destroyed. Autogroup sizing and IDA allocation errors can produce `-ENOSPC` despite table capacity if accounting drifts. Duplicate-match pending rules are subtle: pending children are committed only when the active FTE is deleted. Namespace mode changes are only safe at init time and currently restricted to root FDB namespaces. `mlx5_fs_set_root_dev()` requires empty RDMA transport namespaces before root device migration.

## Test signals

Core tests should cover namespace creation under varied capability sets, flow table create/destroy ordering, root update with underlay QPN lists, flow group creation and autogroup allocation, FTE append and `NO_APPEND` duplicate behavior, rule deletion with counters and forwarding destinations, `FWD_NEXT_PRIO/NS` rewrites, vport ACL namespace add/remove, devlink mode validation/set/get, modify-header/reformat/definer lifecycle, RDMA transport root device migration, and cleanup leak detection. Lockdep, KASAN, fault injection on command providers, and firmware command tracing are especially useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fs_core.c -->
