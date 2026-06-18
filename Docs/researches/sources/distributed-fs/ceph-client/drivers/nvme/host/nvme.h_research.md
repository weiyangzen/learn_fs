# sources/distributed-fs/ceph-client/drivers/nvme/host/nvme.h

## Purpose
This header is the central private contract for the Linux NVMe host stack. It defines shared controller, subsystem, namespace, namespace-head, request, quirk, and operation structures; declares workqueues and core helper APIs; and provides inline helpers used by PCI, fabrics, multipath, ioctl, hwmon, authentication, zoned, and core code.

## Important APIs, Types, And Functions
Major types are `struct nvme_request`, `struct nvme_ctrl`, `struct nvme_subsystem`, `struct nvme_ns_ids`, `struct nvme_ns_head`, `struct nvme_ns`, `struct nvme_ctrl_ops`, `struct nvme_fault_inject`, and `struct nvme_zone_info`. Important enums include `enum nvme_quirks`, `enum nvme_ctrl_state`, `enum nvme_ctrl_flags`, `enum nvme_iopolicy`, namespace feature bits, and `nvme_submit_flags_t`.

Key inline helpers include `nvme_req()`, `nvme_req_qid()`, `nvme_ctrl_state()`, `nvme_ns_head_multipath()`, `nvme_ns_has_pi()`, `nvme_get_virt_boundary()`, command ID generation/extraction helpers, `nvme_find_rq()`, `nvme_strlen()`, `nvme_print_device_info()`, `nvme_reset_subsystem()`, LBA/sector conversion, `nvme_bytes_to_numd()`, `from0based()`, `nvme_is_ana_error()`, `nvme_is_path_error()`, `nvme_try_complete_req()`, `nvme_get_ctrl()`, `nvme_put_ctrl()`, `nvme_is_aen_req()`, `nvme_state_terminal()`, `nvme_req_op()`, `nvme_check_ready()`, `nvme_is_unique_nsid()`, `nvme_ctrl_use_ana()`, `nvme_disk_is_ns_head()`, `nvme_get_ns_from_dev()`, `nvme_start_request()`, `nvme_ctrl_sgl_supported()`, `nvme_ctrl_meta_sgl_supported()`, and `nvme_multi_css()`.

The header declares controller lifecycle APIs, queue freeze/quiesce APIs, passthrough/ioctl APIs, multipath APIs, hwmon APIs, auth APIs, zoned APIs, char-device helpers, command execution helpers, namespace lookup/refcount helpers, and exported attribute groups/operation tables.

## Control Flow
The header does not run standalone control flow, but it defines the shared state machine and call graph shape. Transports allocate a `struct nvme_ctrl`, provide `struct nvme_ctrl_ops`, call `nvme_init_ctrl()` / `nvme_add_ctrl()`, allocate admin and I/O tag sets, and transition controller state through `NVME_CTRL_NEW`, `CONNECTING`, `LIVE`, reset/delete states, and terminal states. Request paths use `struct nvme_request` as the common request-private prefix, initialize commands, call transport-specific queueing, then complete through `nvme_try_complete_req()`, `nvme_complete_rq()`, or batch completion.

Namespace code groups paths by `struct nvme_ns_head`; multipath builds on the optional fields under `CONFIG_NVME_MULTIPATH`. ioctl and io_uring paths use declared passthrough functions and command effects helpers. hwmon and auth are compiled as real hooks or no-op stubs depending on configuration.

## State And Persistence
`struct nvme_ctrl` is the main persistent runtime object. It stores controller identity, queues, device nodes, subsystem linkage, capabilities, limits, feature fields, work items, keepalive state, firmware activation work, fault injection, quirks, fabrics options, discard page state, optional ANA state, optional authentication state, TLS key identity, power-saving configuration, PCI-only host memory buffer fields, and namespace lists.

`struct nvme_subsystem` persists subsystem identity and shared namespace heads across controllers. `struct nvme_ns_head` stores identifiers, format information, features, cdev/disk, shared path list, and optional multipath state. `struct nvme_ns` stores per-controller namespace state, queue/disk, path sibling linkage, flags, cdev, and fault injection. `struct nvme_request` persists per-request command pointer, result, generation counter, retry count, flags, status, optional multipath accounting time, and controller pointer.

Most state is in-memory kernel state rebuilt from identify/log data and transport discovery. Some fields mirror device persistent configuration or capabilities, but this header itself only defines storage and APIs.

## Dependencies And Integration Points
The header includes Linux NVMe UAPI, cdev, PCI, kref, blk-mq, SED OPAL, fault injection, RCU/SRCU, waitqueues, T10 PI, ratelimit, and block trace headers. It is included across NVMe host source files and therefore forms the integration point between transport drivers, core, sysfs, block layer, char devices, multipath, hwmon, authentication, and zoned support.

`struct nvme_ctrl_ops` is the primary transport integration interface. It supplies register access, reset/delete/free behavior, async event submission, subsystem reset, address formatting, device info printing, P2P DMA support, and virtual boundary behavior. Feature-specific sections use `#ifdef` stubs so callers can compile regardless of configuration.

## Risks
This header has high blast radius. Layout changes to `struct nvme_request` are especially risky because transports require it to be the first member of request-private data. Changes to `struct nvme_ctrl`, `nvme_ns_head`, or `nvme_ns` affect many lifecycle paths and can break assumptions about locking, SRCU, or object ownership.

Inline helpers encode behavior, not just declarations. `nvme_try_complete_req()` increments command generation, stores status/result, performs fault injection, handles fake timeouts, and may complete remotely. `nvme_check_ready()` changes behavior for fabrics controllers in `NVME_CTRL_DELETING`. `nvme_is_unique_nsid()` controls whether multipath head disks may be created for private namespaces. Seemingly small edits can alter request completion, failover, or userspace-visible devices.

Configuration stubs must match real function signatures. Mismatches can hide compile coverage when features are disabled. Several fields are conditionally present under `CONFIG_NVME_MULTIPATH`, `CONFIG_NVME_HWMON`, `CONFIG_NVME_HOST_AUTH`, fault injection, and zoned block support, so structure users must stay inside the right guards.

## Test Signals
Build coverage should include representative configurations: with and without multipath, hwmon, host authentication, zoned block, fault injection, SED OPAL, and architectures with `CONFIG_ARCH_NO_SG_CHAIN`. Runtime tests should cover controller state transitions, reset/delete races, request timeout and completion generation counters, namespace add/remove, char and block device lifetime, multipath failover, hwmon init/exit, auth stubs versus real auth, command effects, and zoned operations.

Static analysis should check request-private layout assumptions, missing `#ifdef` guards, stale prototypes, enum/string mapping drift for quirks, and inline helpers that dereference optional fields. Lockdep, KASAN, refcount, and SRCU diagnostics are important because this header defines the shared objects used by most NVMe host concurrency paths.
