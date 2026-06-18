# subset-b-003959 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.c

## Purpose

`ib_srp.c` implements the Linux InfiniBand/RDMA SCSI RDMA Protocol initiator. It registers an RDMA client and SCSI transport, exposes `infiniband_srp` class devices for each local RDMA port, accepts target definitions through the `add_target` sysfs attribute, connects to SRP targets with either IB CM/path-record lookup or RDMA CM/IP routing, then translates SCSI midlayer commands into SRP information units and RDMA buffer descriptors.

## Important APIs, Types, and Functions

The main external integrations are `srp_attach_transport()`, `ib_register_client()`, `ib_sa_path_rec_get()`, `ib_create_cm_id()`, `rdma_create_id()`, `scsi_host_alloc()`, `srp_rport_add()`, and the `scsi_host_template` callbacks. Module parameters control SG limits, memory registration policy, timeout behavior, immediate data, and channel count. Important internal flows include `srp_add_one()`/`srp_remove_one()` for HCA lifetime, `add_target_store()` for target creation, `srp_new_cm_id()`, `srp_create_ch_ib()`, `srp_connect_ch()`, `srp_send_req()`, `srp_cm_rep_handler()`, `srp_queuecommand()`, `srp_map_data()`, `srp_recv_done()`, `srp_process_rsp()`, `srp_rport_reconnect()`, and SCSI EH callbacks `srp_abort()`, `srp_reset_device()`, and `srp_reset_host()`.

## Control Flow

Module initialization validates SRP IU layout sizes, clamps module parameters, creates the remove workqueue, attaches the SRP transport, registers the `infiniband_srp` class, registers an SA client, and registers as an RDMA client. When an RDMA device appears, `srp_add_one()` allocates a protection domain, chooses fast-registration capabilities and global-rkey policy, then creates one `srp_host` class device per RDMA port. Writing target options to `add_target` allocates a SCSI host, parses IB CM or RDMA CM parameters, creates one or more channels, resolves paths/routes, creates CQs/QPs, sends SRP login, posts receive IUs, registers an rport, scans LUNs, and marks the target live.

For normal I/O, `srp_queuecommand()` selects a channel from the block-mq hardware queue tag, reserves a TX IU and request credit, fills `SRP_CMD`, maps the SCSI SG list, emits direct, indirect, fast-registered, or immediate-data descriptors, DMA-syncs the IU, and posts an IB send. Receive completions dispatch by opcode: `SRP_RSP` completes SCSI commands and returns credits, `SRP_CRED_REQ` and `SRP_AER_REQ` send SRP responses, and transport/QP errors start SRP transport failure timers. Reconnect tears down CM state, recreates QPs, resets outstanding requests, and logs in each channel again.

## State and Persistence Behavior

Long-lived state is split across `srp_device` per HCA, `srp_host` per port, `srp_target_port` per target, and `srp_rdma_ch` per RDMA channel. Each target persists SCSI host/rport state, namespace reference, target identity, queue sizing, retry timeout, work items, and connection state. Each channel persists CQs, QP, CM ID, IU rings, free TX list, request credits, task-management completion state, and optional fast-registration pool. Per-SCSI-command private state persists indirect descriptors, DMA mappings, and fast-registration descriptor pointers until command completion or cleanup.

## Dependencies and Integration Points

The file depends on RDMA core verbs, IB CM, RDMA CM, SA path records, net namespaces, SCSI core, and `scsi_transport_srp`. It consumes SRP wire definitions from `<scsi/srp.h>` and local object layouts from `ib_srp.h`. Sysfs class attributes expose target identity and runtime counters. SCSI transport timers call back into reconnect/delete/terminate hooks. The SCSI EH path depends on SRP task management IUs and on rport state for fast-fail decisions.

## Risks and Edge Cases

The highest-risk areas are concurrent teardown versus completions, request-credit accounting, and memory registration lifetime. `srp_free_ch_ib()` deliberately nulls `ch->target` after CQ/QP destruction to block late SCSI EH use, and `srp_destroy_qp()` drains before destroying to avoid receive callbacks on freed QPs. The fast-registration path must invalidate rkeys and return descriptors exactly once. Immediate data has strict offset and IU-size constraints. Reconnect relies on serialization by the SRP rport mutex. Option parsing must reject incomplete IB/RDMA CM tuples, duplicate targets, oversized SG tables, and bad timeout combinations. Topspin/Cisco workaround behavior intentionally changes login port-ID layout for known legacy targets.

## Test Signals

Useful signals include module load/unload with RDMA devices present, `add_target` success and validation failures for both IB CM and RDMA CM formats, multi-channel login and partial-channel fallback, LUN scan success/removal, direct, indirect, external SG, fast-registration, global-rkey, and immediate-data I/O, request-credit exhaustion and recovery, SCSI abort/LUN reset/host reset, target logout/disconnect, QP error injection, reconnect after link loss, sysfs attribute reads, namespace cleanup, and builds with fast registration unavailable or disabled by module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.h

## Purpose

`ib_srp.h` defines the in-kernel state model for the SRP initiator implemented by `ib_srp.c`. It is the contract between connection setup, SCSI command dispatch, RDMA completions, fast memory registration, and target removal logic.

## Important APIs, Types, and Functions

The header defines SRP constants for path and abort timeouts, redirect status codes, default queue and SG sizes, immediate-data layout, and special tags. Core enums are `srp_target_state` and `srp_iu_type`. Core structures are `srp_device`, `srp_host`, `srp_request`, `srp_rdma_ch`, `srp_target_port`, `srp_iu`, `srp_fr_desc`, `srp_fr_pool`, and `srp_map_state`.

## Control Flow

There are no functions in the header, but the structure layout describes runtime flow. `srp_device` is created from RDMA client add callbacks and owns HCA-level registration capability and PD state. `srp_host` represents a local port and owns target lists and the `add_target` entry. `srp_target_port` is created per target definition, then owns channels, SCSI host/rport state, target identifiers, queue sizing, and work items. `srp_rdma_ch` is the hot-path object used by SCSI queuecommand, send/receive completions, CM callbacks, and reconnect.

## State and Persistence Behavior

The header separates hot-path fields from less frequently used fields in `srp_rdma_ch` and `srp_target_port`. Persistent state includes CM IDs, path records, QPs/CQs, IU rings, request credits, task-management state, target identity, network namespace, and queued work. `srp_fr_pool` persists a free-list of MRs for fast registration. `srp_request` persists per-command DMA and descriptor state until command-private cleanup.

## Dependencies and Integration Points

It includes Linux list, mutex, scatterlist, SCSI host/command, RDMA verbs, SA, IB CM, and RDMA CM headers. It depends on `<scsi/srp.h>` indirectly through the C file for SRP wire structures. The structures are embedded in SCSI host private data, SCSI command private data, RDMA CM contexts, CQ contexts, and work items.

## Risks and Edge Cases

Cacheline-sensitive fields are explicitly grouped; careless layout churn can hurt I/O path performance. Several fields are shared across interrupt/completion context and process context, so their lock ownership matters. `union` CM state is selected by `using_rdma_cm`; mixing the wrong branch can corrupt connection teardown. The counted flexible array in `srp_fr_pool` must match allocation size. `srp_map_state` has union members reused by FR and generic mapping flows, so each mapping path must initialize the right branch.

## Test Signals

Compile coverage catches most type drift. Runtime coverage should exercise all structures through target add/remove, reconnect, task management, fast-registration allocation/exhaustion, immediate data, multi-channel I/O, and SCSI command-private init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srp/ib_srp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Kconfig

## Purpose

This Kconfig entry controls whether the InfiniBand SCSI RDMA Protocol target driver is built. It exposes `CONFIG_INFINIBAND_SRPT` as a tristate option for built-in, module, or disabled SRPT target support.

## Important APIs, Types, and Functions

The symbol is `INFINIBAND_SRPT`, prompted as "InfiniBand SCSI RDMA Protocol target support". It depends on `INFINIBAND`, `INFINIBAND_ADDR_TRANS`, and `TARGET_CORE`.

## Control Flow

There is no runtime control flow. During configuration, the option is visible only when RDMA core address translation and LIO target core are available. Kbuild then uses the symbol to include `ib_srpt.o`.

## State and Persistence Behavior

The only persisted state is kernel build configuration. If enabled as a module, the resulting module is the SRPT target driver; if built in, it links into the kernel image.

## Dependencies and Integration Points

The dependency list matches `ib_srpt.c` integrations with RDMA/IB core, RDMA address management, and target-core fabric APIs. The help text documents SRP target behavior and notes RDMA transport coverage.

## Risks and Edge Cases

Dependency drift is the main risk: if `ib_srpt.c` starts requiring additional kernel subsystems, the Kconfig gate must be updated or build failures will appear in partial configurations. The help text mentions iWARP even though device-management MAD behavior is InfiniBand-specific and RDMA CM support is controlled at runtime/configfs.

## Test Signals

Build matrix checks should cover `CONFIG_INFINIBAND_SRPT=y`, `=m`, and disabled, plus dependency-disabled combinations for `INFINIBAND`, `INFINIBAND_ADDR_TRANS`, and `TARGET_CORE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Makefile

## Purpose

The SRPT Makefile connects the Kconfig symbol to the driver object.

## Important APIs, Types, and Functions

`obj-$(CONFIG_INFINIBAND_SRPT) += ib_srpt.o` tells Kbuild to compile and link `ib_srpt.c` when SRPT is enabled.

## Control Flow

There is no runtime flow. Kbuild evaluates `CONFIG_INFINIBAND_SRPT` and either omits the object, links it built-in, or emits it as a module.

## State and Persistence Behavior

The file affects build artifacts only. It creates no runtime state.

## Dependencies and Integration Points

It integrates with the surrounding RDMA ULP build tree and depends on `Kconfig` to ensure required subsystems are available before `ib_srpt.o` is selected.

## Risks and Edge Cases

Adding more translation units to SRPT without updating this file would omit code. Renaming `ib_srpt.c` without changing the object rule would break the build.

## Test Signals

`make M=drivers/infiniband/ulp/srpt` and full kernel builds with `CONFIG_INFINIBAND_SRPT=m` and `=y` should produce/link the expected object without unresolved RDMA or target-core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_dm_mad.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_dm_mad.h

## Purpose

`ib_dm_mad.h` defines the InfiniBand Device Management MAD structures and constants used by the SRPT target to advertise SRP I/O controller information through management datagrams.

## Important APIs, Types, and Functions

The header defines device-management MAD status values, attribute IDs for `ClassPortInfo`, `IOUnitInfo`, `IOControllerProfile`, and `ServiceEntries`, and packed protocol-facing structures `ib_dm_hdr`, `ib_dm_mad`, `ib_dm_iou_info`, `ib_dm_ioc_profile`, `ib_dm_svc_entry`, and `ib_dm_svc_entries`.

## Control Flow

The header has no functions. `ib_srpt.c` receives a device-management MAD, creates a reply MAD, switches on `mad_hdr.attr_id`, and fills these structures with `srpt_get_class_port_info()`, `srpt_get_iou()`, `srpt_get_ioc()`, or `srpt_get_svc_entries()`.

## State and Persistence Behavior

The structures are transient wire-format payloads. They persist only inside received and transmitted MAD buffers. Their field layout must remain compatible with InfiniBand device-management definitions and SRP discovery expectations.

## Dependencies and Integration Points

It includes `<rdma/ib_mad.h>` for MAD header sizes and base structures. `ib_srpt.h` includes this file so the SRPT source can cast `ib_dm_mad.data` to the appropriate payload type. The 64-byte header invariant is checked in `ib_srpt.c` before creating send MADs with `IB_MGMT_DEVICE_HDR`.

## Risks and Edge Cases

The main risk is ABI/layout drift: MAD payloads are parsed by remote management clients, so field order, endian types, and header size are part of the protocol. ServiceEntries supports four entries structurally, while SRPT currently fills one. Status values must be returned in big-endian MAD status fields.

## Test Signals

MAD discovery tests should query each supported attribute, invalid attributes, invalid IOC slots, unsupported SET methods, service-entry ranges, and verify payload sizes, endian values, status codes, SRP service names, and advertised RDMA/send limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_dm_mad.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.c

## Purpose

`ib_srpt.c` implements the Linux SRP target fabric driver for target core. It advertises SRP target ports through InfiniBand Device Management MADs, accepts SRP login over IB CM or RDMA CM, creates target-core sessions, receives SRP commands, performs RDMA reads/writes through `rdma_rw`, and sends SRP responses.

## Important APIs, Types, and Functions

Module parameters are `srp_max_req_size`, `srpt_srq_size`, and `srpt_service_guid`. HCA lifetime is handled by `srpt_add_one()` and `srpt_remove_one()`. Discovery is handled by `srpt_refresh_port()`, MAD registration, and `srpt_mad_recv_handler()`. Login and connection management are centered on `srpt_cm_req_recv()`, `srpt_cm_handler()`, `srpt_rdma_cm_handler()`, `srpt_cm_rtu_recv()`, `srpt_disconnect_ch()`, and `srpt_release_channel_work()`. I/O is handled by `srpt_recv_done()`, `srpt_handle_new_iu()`, `srpt_handle_cmd()`, `srpt_get_desc_tbl()`, `srpt_write_pending()`, `srpt_queue_response()`, and `srpt_send_done()`. Configfs target-fabric operations are collected in `srpt_template`.

## Control Flow

Initialization validates request and SRQ sizes, registers the target-core fabric template, then registers an RDMA client. Device add allocates a `srpt_device`, PD, optional SRQ, IB CM listener, event handler, and per-port `srpt_port` objects, then refreshes each port to cache LID/GID names and register a MAD agent. Configfs `fabric_make_wwn` and `fabric_make_tpg` map target-core portal groups to discovered RDMA port names, and enabling a TPG allows login.

For login, IB CM or RDMA CM request handlers normalize private data into `srp_login_req`, validate IU length, target enablement, and target port ID, create or find a nexus, allocate a channel, CQs/QP, send/receive context rings, target-core session, and response/reject payloads. The channel is added to the nexus, moved through RTR/RTS or RDMA-CM-established state, and a zero-length write triggers wait-list processing after the channel becomes live. Received SRP commands are parsed into target-core commands with scatterlists from direct, indirect, or immediate descriptors. Target core calls back for write-pending RDMA reads, data-in/status responses, task-management responses, aborts, and command release.

## State and Persistence Behavior

Global state includes the SRPT device list, shared memory-cache xarray, service GUID, RDMA CM listen port/ID, and locks. Per-HCA `srpt_device` state persists PD/lkey, optional SRQ, receive ring, event handler, and per-port array. Per-port state persists enablement, cached LID/GID/name data, target-core port IDs, configfs attributes, nexus list, and channel refcount. Per-channel state persists CM ID, QP/CQ, session pointer, request/response rings, send-queue credits, SRP request credits, command wait list, channel state, and release work. Per-command `srpt_send_ioctx` tracks target-core command state, RDMA contexts, immediate data receive ownership, and sense data.

## Dependencies and Integration Points

The file integrates RDMA verbs, IB MAD, IB CM, RDMA CM, `rdma_rw`, target-core fabric APIs, SCSI protocol definitions, and local SRPT/SRP wire structures. It registers `target_core_fabric_ops` named `srpt`, creates configfs attributes for RDMA CM port and TPG tuning, and depends on target-core session/tag management for command lifetimes. Port discovery and service advertisement depend on `ib_dm_mad.h`.

## Risks and Edge Cases

Concurrency and lifetime management are the dominant risks. Channel state is monotonic and protected by `spinlock`, but close paths can be entered from CM callbacks, configfs disable, session close, and QP completions. The zero-length write drain mechanism must run before freeing QP/CQ and rings. SRQ toggling disables the port and logs out sessions, but global SRQ state is per-HCA while the config attribute is per-port. Login rejection paths must not leak CM IDs after ownership transfer. Immediate-data buffers require 512-byte alignment and careful receive-buffer reposting after target command release. Request-limit and send-queue accounting must remain balanced across normal responses, aborts, failed sends, and delayed wait-list processing.

## Test Signals

Useful tests include module load/unload, RDMA device add/remove, configfs WWN/TPG create/drop/enable/disable, MAD GETs for all supported attributes, IB CM and RDMA CM login, invalid login length/target ID/disabled TPG rejection, multichannel relogin behavior, SRQ on/off transitions, direct/indirect/immediate SRP command descriptors, write-pending RDMA read, read data-in RDMA write, sense/residual response formatting, task management, initiator disconnect, target disable with live sessions, QP error/drain behavior, and KASAN/KCSAN/leak checks across rejection and teardown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.h

## Purpose

`ib_srpt.h` defines SRPT target constants, command/channel state machines, and object layouts shared by SRPT connection management, RDMA I/O, MAD discovery, and target-core configfs integration.

## Important APIs, Types, and Functions

The header defines SRP target discovery constants, login flag masks, solicited-notification bits, task-management statuses, command task attributes, queue-size bounds, request/response size bounds, immediate-data limits, and default RDMA limits. Important types include `srpt_command_state`, `rdma_ch_state`, `srpt_ioctx`, `srpt_recv_ioctx`, `srpt_rw_ctx`, `srpt_send_ioctx`, `srpt_rdma_ch`, `srpt_nexus`, `srpt_port_attrib`, `srpt_tpg`, `srpt_port_id`, `srpt_port`, and `srpt_device`.

## Control Flow

The header has no executable code. Its objects define the control path used by `ib_srpt.c`: HCA add creates `srpt_device` and `srpt_port`; configfs creates `srpt_port_id` and `srpt_tpg`; login creates or finds a `srpt_nexus` and allocates `srpt_rdma_ch`; receives allocate `srpt_recv_ioctx`; accepted commands allocate `srpt_send_ioctx`; RDMA transfers allocate `srpt_rw_ctx`; target-core callbacks advance `srpt_command_state`; CM and drain paths advance `rdma_ch_state`.

## State and Persistence Behavior

`srpt_device` persists HCA-level PD, lkey, SRQ, event handler, receive buffers, and ports. `srpt_port` persists enablement, cached addressing, names, configfs IDs, attributes, nexus list, and live-channel refcount. `srpt_rdma_ch` persists QP/CQ, CM ID union, session, rings, credits, wait list, state, and release work. `srpt_send_ioctx` persists one target-core command and its RDMA context until `release_cmd`.

## Dependencies and Integration Points

It includes RDMA verbs, SA, IB CM, RDMA CM, RDMA read/write helper APIs, SCSI SRP wire definitions, and `ib_dm_mad.h`. Structures embed target-core `se_cmd`, `se_session`, `se_portal_group`, and `se_wwn` types through source includes, and are used as CM/QP/CQ contexts.

## Risks and Edge Cases

The channel state enum relies on increasing numerical order for monotonic transitions. Send and receive rings are sized from runtime limits and cache sizes; mismatches can corrupt DMA buffers. The CM ID union is selected by `using_rdma_cm`. `srpt_send_ioctx.recv_ioctx` transfers receive-buffer ownership for immediate data and must be cleared before repost. Per-port `use_srq` attributes drive per-device SRQ allocation, so multi-port expectations need care.

## Test Signals

Compile and runtime tests should cover all command and channel states, SRQ and non-SRQ modes, target-core session lifecycle, configfs port/TPG objects, direct/indirect/immediate descriptors, RDMA read/write contexts, and disconnect/free ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/ulp/srpt/ib_srpt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/Kconfig

## Purpose

This Kconfig file defines the top-level Linux input subsystem menu, core input options, userland interfaces, helper libraries, KUnit tests, the APM power bridge option, and includes lower-level driver family Kconfig files.

## Important APIs, Types, and Functions

Top-level `config INPUT` enables the generic input layer. Helper/interface options include `INPUT_LEDS`, `INPUT_FF_MEMLESS`, `INPUT_SPARSEKMAP`, `INPUT_MATRIXKMAP`, `INPUT_VIVALDIFMAP`, `INPUT_MOUSEDEV`, `INPUT_MOUSEDEV_PSAUX`, `INPUT_MOUSEDEV_SCREEN_X`, `INPUT_MOUSEDEV_SCREEN_Y`, `INPUT_JOYDEV`, `INPUT_EVDEV`, `INPUT_KUNIT_TEST`, and `INPUT_APMPOWER`.

## Control Flow

There is no runtime control flow. Kconfig shows the input menu, conditionally exposes most options only inside `if INPUT`, sources keyboard, mouse, joystick, tablet, touchscreen, misc, RMI4, serio, and gameport menus, and records selected values into `.config`. The Makefile consumes those symbols to build the input core, handlers, libraries, tests, and subdirectories.

## State and Persistence Behavior

The file persists build configuration state. Screen resolution defaults for mousedev become configuration constants, and tristate settings determine whether components are built-in, modules, or omitted.

## Dependencies and Integration Points

It integrates input core with LED class support, APM emulation, KUnit, userland device interfaces, and hardware-specific input submenus. `INPUT_APMPOWER` depends on `INPUT` and `APM_EMULATION` and maps to `apm-power.o`.

## Risks and Edge Cases

Hidden helper symbols such as `INPUT_VIVALDIFMAP` rely on drivers selecting them. `INPUT` defaults to yes but can be hidden unless `EXPERT` is enabled. Dependency drift between driver source and Kconfig can create invalid build combinations. APM power bridging is expert-only because it can suspend systems directly from input events.

## Test Signals

Build matrix checks should cover built-in and modular input core, evdev/mousedev/joydev variants, helper-library selection by downstream drivers, KUnit enablement, `INPUT_APMPOWER` with and without `APM_EMULATION`, and successful descent into all sourced submenus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/Makefile

## Purpose

The input Makefile maps input subsystem Kconfig symbols to core objects, helper modules, userland handlers, tests, and hardware driver subdirectories.

## Important APIs, Types, and Functions

`obj-$(CONFIG_INPUT) += input-core.o` builds the composite core from `input.o`, `input-compat.o`, `input-mt.o`, `input-poller.o`, `ff-core.o`, `touchscreen.o`, and `touch-overlay.o`. Other rules build `ff-memless.o`, sparse/matrix/vivaldi keymap helpers, LED/mouse/joystick/event handlers, input tests, `apm-power.o`, RMI4 core, and hardware subdirectories.

## Control Flow

There is no runtime flow. Kbuild expands enabled symbols into objects and subdirectories. Built-in symbols link into the kernel image, while modular symbols produce modules where allowed by the surrounding Kconfig.

## State and Persistence Behavior

The Makefile affects build artifacts only. The composite object list determines which core input features are always present when `CONFIG_INPUT` is enabled.

## Dependencies and Integration Points

It consumes symbols from `drivers/input/Kconfig` and hardware-family Kconfig files. It is the build bridge from top-level input configuration to subdirectories such as `keyboard/`, `mouse/`, `touchscreen/`, `misc/`, `serio/`, and `gameport/`.

## Risks and Edge Cases

Adding a source file without updating the composite list or symbol rule silently omits code. Renaming objects without updating rules breaks builds. Subdirectory rules depend on matching Kconfig symbols such as `CONFIG_INPUT_KEYBOARD` and `CONFIG_RMI4_CORE`.

## Test Signals

Useful checks include `make M=drivers/input`, full builds with `CONFIG_INPUT=y` and `=m`, modular builds for handlers/helpers, KUnit input test builds, `CONFIG_INPUT_APMPOWER=m`, and hardware subdirectory selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/apm-power.c -->
# sources/distributed-fs/ceph-client/drivers/input/apm-power.c

## Purpose

`apm-power.c` is a small input handler that bridges input power events to APM emulation. It listens for `EV_PWR` events and converts `KEY_SUSPEND` key-down events into `APM_USER_SUSPEND` requests.

## Important APIs, Types, and Functions

`system_power_event()` maps keycodes to APM actions. `apmpower_event()` filters input events to key-down power events. `apmpower_connect()` allocates and registers an `input_handle` and opens matching devices. `apmpower_disconnect()` closes and frees the handle. `apmpower_ids` matches devices advertising `EV_PWR`. `apmpower_handler` registers the handler with input core through `input_register_handler()` and `input_unregister_handler()`.

## Control Flow

On module load, `apmpower_init()` registers the input handler. Input core calls `apmpower_connect()` for matching devices, which registers a handle and opens the device. During event delivery, only value `1` key-down events are processed; `EV_PWR` plus `KEY_SUSPEND` queues an APM user suspend event and logs the request. On disconnect or module exit, handles are closed/unregistered and the handler is removed.

## State and Persistence Behavior

The module has no global mutable driver state beyond the registered `input_handler`. Per-device state is a heap `input_handle` owned from connect until disconnect. Suspend requests are queued into the APM emulation subsystem; this file does not persist policy state.

## Dependencies and Integration Points

It depends on input core, APM emulation, PM headers, and module infrastructure. It is selected by `CONFIG_INPUT_APMPOWER`, which depends on `INPUT` and `APM_EMULATION`, and is built by `drivers/input/Makefile` as `apm-power.o`.

## Risks and Edge Cases

The driver intentionally bypasses userspace policy for suspend key events, so enabling it can surprise systems that expect desktop/session-manager handling. It only handles `KEY_SUSPEND`; other power keys are ignored. It only reacts to key-down value `1`, not repeats or releases. Connect error paths must unregister and free the handle correctly, which the code does.

## Test Signals

Tests should cover module load/unload, matching an input device with `EV_PWR`, connect/open failure paths, synthetic `KEY_SUSPEND` down/repeat/up events, verification that exactly key-down queues `APM_USER_SUSPEND`, non-suspend power keys being ignored, and disconnect cleanup under input device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/apm-power.c -->
