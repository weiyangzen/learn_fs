# Research: subset-b-004989

This grouped report covers NVMe host transport and support files under `sources/distributed-fs/ceph-client/drivers/nvme/host`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/pci.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/pci.c

## Purpose

`pci.c` is the Linux NVMe PCIe host transport driver. It binds PCI devices in the NVMe class or explicit quirk table, maps the controller BAR, creates admin and I/O queues, translates blk-mq requests into NVMe submission queue entries, maps request data and metadata through DMA, handles completions through interrupts or polling, and coordinates controller reset, shutdown, suspend/resume, and PCI error recovery. It is the hardware-facing transport implementation behind the generic `nvme_ctrl` core for local PCIe NVMe devices.

## Important APIs, types, and functions

- Module parameters shape runtime behavior: `use_threaded_interrupts`, `use_cmb_sqes`, `max_host_mem_size_mb`, `sgl_threshold`, `io_queue_depth`, `write_queues`, `poll_queues`, `noacpi`, and `quirks`.
- `struct nvme_dev` is the per-PCI-function transport object. It embeds `struct nvme_ctrl`, blk-mq tag sets, MMIO BAR pointers, doorbell stride, queue counts, CMB/HMB state, shadow doorbell buffers, descriptor pools, and shutdown serialization.
- `struct nvme_queue` represents an admin or I/O queue pair with SQ/CQ DMA memory, doorbell pointers, phase/head/tail indices, IRQ vector, poll lock, and queue flags such as `NVMEQ_ENABLED`, `NVMEQ_SQ_CMB`, and `NVMEQ_POLLED`.
- `struct nvme_iod` is blk-mq request private data. It stores the prepared NVMe command, descriptor pointers, DMA iterator state, metadata mapping state, and flags that tell completion paths how to unmap resources.
- Request mapping is split across `nvme_prep_rq`, `nvme_map_data`, `nvme_pci_setup_data_simple`, `nvme_pci_setup_data_prp`, `nvme_pci_setup_data_sgl`, `nvme_map_metadata`, `nvme_pci_setup_meta_mptr`, and `nvme_pci_setup_meta_iter`.
- Submission and batching are handled by `nvme_queue_rq`, `nvme_queue_rqs`, `nvme_submit_cmds`, `nvme_sq_copy_cmd`, `nvme_write_sq_db`, and `nvme_commit_rqs`.
- Completion handling is centered on `nvme_irq`, `nvme_poll`, `nvme_poll_cq`, `nvme_handle_cqe`, `nvme_pci_complete_rq`, and `nvme_pci_complete_batch`.
- Queue lifecycle is implemented by `nvme_alloc_queue`, `nvme_create_queue`, `nvme_setup_io_queues`, `nvme_create_io_queues`, `nvme_delete_io_queues`, `nvme_suspend_queue`, and `nvme_free_queues`.
- Controller lifecycle is implemented by `nvme_probe`, `nvme_pci_enable`, `nvme_pci_configure_admin_queue`, `nvme_reset_work`, `nvme_dev_disable`, `nvme_remove`, `nvme_shutdown`, and the PM and PCI error handler callbacks.
- The `nvme_pci_ctrl_ops` vtable connects this transport to the NVMe core through register access, async event submission, subsystem reset, address reporting, P2PDMA support, and virtual boundary reporting.

## Control flow

Probe starts in `nvme_probe`. The driver allocates `nvme_dev`, applies static, DMI, ACPI, and user-specified quirks, initializes the generic controller, maps PCI BAR0, allocates the I/O descriptor mempool, enables the PCI device, configures the admin queue, allocates the admin blk-mq tag set, marks the controller `CONNECTING`, finishes generic controller initialization, allocates optional doorbell buffers and host memory buffer, sets up I/O queues, optionally creates the I/O tag set, marks the controller `LIVE`, starts scans/events, and returns with the controller registered.

For I/O, blk-mq calls `nvme_queue_rq` or `nvme_queue_rqs`. The transport first checks queue enabled state and controller readiness, then `nvme_prep_rq` calls the core `nvme_setup_cmd`, maps data and integrity metadata, and starts the request. The SQE is copied into the submission ring under `sq_lock`; the driver writes a real or shadow doorbell when the batch requires it or the next command would wrap. Batched submission groups requests by hardware queue before ringing the doorbell.

Data mapping chooses between PRP and SGL. Single-segment requests try a fast path using `dma_map_bvec`. Multi-segment requests use blk DMA iterators. SGL is forced for controller page gaps, user commands, and multiple integrity segments; otherwise SGL is selected only when supported and the average segment size exceeds `sgl_threshold`. PRP setup builds one or more PRP list pages from DMA pool descriptors. SGL setup builds a data or segment descriptor list. Metadata uses MPTR for trusted single-segment kernel integrity data where possible, and metadata SGLs for user commands, P2P cases, or multi-segment integrity.

Completion flow starts from an IRQ, threaded IRQ check, or blk-mq poll. `nvme_poll_cq` checks the CQE phase bit, uses `dma_rmb`, handles each CQE, advances head/phase, and rings the CQ doorbell. AEN command IDs bypass normal request lookup and go to the core async-event completion path. Normal completions locate the request in the relevant tag set, try the core completion fast path, batch if possible, and finally unmap metadata/data before `nvme_complete_rq`.

Reset and error flow is explicit. Timeouts first poll for a missed interrupt. If a request is still in flight, the driver may submit an admin abort; a repeated abort or admin timeout transitions to controller reset. `nvme_reset_work` disables a previously enabled controller if needed, re-enables PCI/admin queues, repeats core initialization, recreates HMB/doorbell resources and I/O queues, updates queue counts, and either returns to `LIVE` or marks namespaces dead and the controller `DEAD`. PCI AER callbacks quiesce and disable queues on frozen channels and schedule reset after slot reset.

## State and persistence behavior

Persistent state is mostly kernel-resident controller and queue state. `nvme_dev` persists for the lifetime of the PCI binding, while controller-visible state includes admin/I/O queue registers, doorbell memory, optional controller memory buffer mappings, and optional host memory buffer descriptors. The driver stores HMB allocations across resets when reusable and tells the controller with `NVME_HOST_MEM_RETURN`; it frees them on teardown or explicit sysfs disable.

Queue state is volatile and recreated during reset. `online_queues`, `queue_count`, `max_qid`, queue flags, CQ phase, SQ/CQ indices, and IRQ vector allocations are reinitialized when queues are created. Shadow doorbell buffers are DMA coherent memory tied to the number of allocated queues; they are zeroed before reuse so stale values are not exposed to a new controller instance.

The module-level dynamic quirk list is persistent until module unload and is freed in `nvme_exit`. Suspend state records `last_ps` to restore a host-managed power state on resume when the driver chooses protocol-level suspend rather than full controller shutdown.

## Dependencies and integration points

This file depends on the NVMe core interfaces in `nvme.h`, tracepoints, blk-mq, blk-integrity, DMA mapping helpers, PCI core, IRQ affinity, P2PDMA, ACPI/DMI quirk detection, kernel PM, and PCI error recovery. It exports no direct application API; it registers a `pci_driver` named `nvme` and uses `nvme_ctrl_ops` plus blk-mq ops as integration surfaces.

The sysfs groups are a composition of generic NVMe attributes from `sysfs.c` and PCI-specific CMB/HMB attributes declared here. Core functions such as `nvme_init_ctrl`, `nvme_init_ctrl_finish`, `nvme_start_ctrl`, `nvme_remove_namespaces`, `nvme_alloc_admin_tag_set`, `nvme_alloc_io_tag_set`, `nvme_complete_rq`, and `nvme_check_ready` define much of the contract.

## Risks and edge cases

- DMA mapping/unmapping is complex. Incorrect `iod` flags, descriptor counts, or failure cleanup can leak DMA mappings, double-free descriptor pool entries, or corrupt device-visible PRP/SGL chains.
- PRP list construction depends on NVMe controller page alignment and bounded descriptor counts. Bad assumptions around segment gaps or maximum transfer size can produce invalid commands.
- Reset paths must coordinate blk-mq freezing, queue quiescing, IRQ freeing, BAR remapping, and PCI disable. Races between timeout, remove, reset, and error recovery are high-risk.
- Doorbell buffer ordering relies on `wmb`/`mb` and controller-side ordering. Relaxing barriers can lose queue notifications.
- CMB and P2PDMA paths depend on BAR alignment, resource sizing, and peer memory support. CMB queue allocation must safely fall back to host memory.
- HMB setup tolerates allocation failure, but reuse and sysfs toggling must keep descriptor memory and controller feature state synchronized.
- Quirk handling is essential for real devices. Changes to quirk masks, queue sizes, MSI behavior, or suspend choices can regress specific SSD and platform combinations.

## Test signals

Useful validation signals include successful module probe and namespace discovery; admin and I/O queue creation counts in logs; blk-mq read/write, discard, write-zeroes, passthrough, and integrity workloads; IRQ and polled I/O completion coverage; suspend/resume across APST and simple-suspend quirked systems; hot remove and PCI AER recovery; reset during active I/O; HMB sysfs enable/disable; CMB presence and fallback; P2PDMA-capable DMA paths; and fault injection around DMA allocation, queue creation, interrupts, and admin command failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/pr.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/pr.c

## Purpose

`pr.c` implements the block-layer persistent reservation operations for NVMe namespaces. It translates Linux `pr_ops` requests into NVMe reservation register, acquire, release, and report commands, handles both single namespace disks and multipath namespace-head disks, converts NVMe status values into block persistent-reservation status codes, and parses reservation report payloads back into block-layer key and held-reservation structures.

## Important APIs, types, and functions

- `nvme_pr_ops` is the exported `struct pr_ops` used by the block layer.
- `nvme_pr_type_from_blk` and `block_pr_type_from_nvme` translate between Linux `enum pr_type` and NVMe `enum nvme_pr_type`.
- `nvme_send_ns_head_pr_command` selects an active path under the namespace head SRCU lock and submits the command to the chosen namespace queue.
- `nvme_send_ns_pr_command` submits a command directly for a concrete `struct nvme_ns`.
- `__nvme_send_pr_command` builds the common NVMe command fields and dispatches to namespace-head or namespace submission.
- `nvme_send_pr_command` wraps dispatch and maps completion status through `nvme_status_to_pr_err`.
- Operation implementations are `nvme_pr_register`, `nvme_pr_reserve`, `nvme_pr_preempt`, `nvme_pr_clear`, `nvme_pr_release`, `nvme_pr_read_keys`, and `nvme_pr_read_reservation`.
- `nvme_pr_resv_report` issues reservation report, initially requesting extended data structures and retrying without EDS on host-ID inconsistency.

## Control flow

Block persistent reservation callers enter through `nvme_pr_ops`. Register, reserve, preempt, clear, and release allocate the matching NVMe reservation data structure on the stack, fill current, new, or preempt keys in little-endian form, compute `cdw10` action/type/ignore-key fields, and submit a synchronous NVMe command. Register uses `NVME_PR_CPTPL_PERSIST`, so the registration asks the controller to persist through power loss where supported.

Read operations use reservation report. `nvme_pr_read_keys` allocates a report buffer sized for the caller's requested number of keys, calls `nvme_pr_resv_report`, copies generation and registered controller count, and copies either extended or legacy registration entries into the output key array. `nvme_pr_read_reservation` first obtains the registration count with a small report, allocates an exact buffer, retries if the count changed between reports, then finds the entry with `rcsts` set to identify the holder key and maps the NVMe reservation type back to the block type.

Multipath dispatch uses `nvme_disk_is_ns_head`. For a namespace-head disk, the code takes `head->srcu`, calls `nvme_find_path`, stamps the namespace ID, and submits to that path queue. If no path is available it returns `-EWOULDBLOCK`. For a non-multipath namespace disk, it uses `bd_disk->private_data` as `struct nvme_ns`.

## State and persistence behavior

The file does not maintain long-lived state of its own. It sends commands that mutate controller-side reservation state and registration keys. The persistent behavior requested by this implementation is most visible in `nvme_pr_register`, where `NVME_PR_CPTPL_PERSIST` is set. Read paths allocate temporary report buffers with `kvzalloc` or `kzalloc`, free them before return, and expose only copied generation/key/type results to the block layer.

The state visible to the code is namespace topology state: namespace-head SRCU protection, active path selection, namespace IDs, and request queues. This topology can change concurrently, which is why namespace-head commands run under SRCU and may fail with no available path.

## Dependencies and integration points

The implementation integrates Linux block persistent reservations (`linux/pr.h` and `struct pr_ops`) with NVMe core command submission (`nvme_submit_sync_cmd`), namespace/multipath helpers (`nvme_disk_is_ns_head`, `nvme_find_path`), NVMe reservation data structures, unaligned access helpers for `regctl`, and NVMe status helpers such as `nvme_is_path_error`.

It depends on NVMe target-format structures named `nvmet_pr_register_data`, `nvmet_pr_acquire_data`, and `nvmet_pr_release_data` for command payload layout, and on NVMe reservation report structures for parsing controller responses.

## Risks and edge cases

- Multipath commands can return `-EWOULDBLOCK` if no path is currently selectable; upper layers must retry or surface path failure appropriately.
- Reservation report supports both extended and non-extended formats. Bugs in the fallback path can misparse keys or holder state.
- `nvme_pr_read_reservation` retries when registration count changes, but a highly unstable reservation set can still cause repeated work.
- Unsupported block PR flags are rejected with `-EOPNOTSUPP`; only `PR_FL_IGNORE_KEY` is allowed where implemented.
- Status conversion must preserve reservation conflicts and path failures distinctly. Mapping too much to generic I/O error would make cluster fencing failures harder to diagnose.
- Large `num_keys` values can overflow report-size calculations; the code guards `rse_len > U32_MAX`.

## Test signals

Exercise block PR ioctl paths over normal and multipath NVMe namespaces. Validate register, replace, ignore-key register, reserve, release, clear, preempt, and preempt-and-abort. Verify reservation conflict status, invalid field/opcode mapping, no-path multipath behavior, EDS and legacy reservation report parsing, holder-key reporting, generation changes, and concurrent registration changes during `read_reservation`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/pr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/rdma.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/rdma.c

## Purpose

`rdma.c` is the NVMe over Fabrics RDMA host transport. It registers the `rdma` fabrics transport, creates controllers from fabrics options, resolves RDMA addresses/routes, creates RDMA CM IDs, completion queues, queue pairs, memory-registration pools, and NVMe queues, maps blk-mq requests into keyed SGL or inline capsules, handles send/receive completions, supports protection information through signature memory regions, and performs reconnect/error recovery for remote NVMe controllers.

## Important APIs, types, and functions

- `struct nvme_rdma_device` wraps an RDMA `ib_device`, protection domain, reference count, and maximum inline segment count. Instances are shared by controllers using the same RDMA device.
- `struct nvme_rdma_queue` represents one fabrics queue with response ring, queue size, command capsule size, RDMA CM ID, QP, CQ, state flags, queue lock, PI support, and CM completion state.
- `struct nvme_rdma_ctrl` embeds `struct nvme_ctrl` and stores queues, admin/I/O blk-mq tag sets, reconnect and error work, async-event SQE, RDMA device, address tuples, max fast-register pages, and queue mapping counts.
- `struct nvme_rdma_request` is request private data. It stores NVMe request/core command state, SQE DMA mapping, result/status, request refcount, send SGEs, memory-registration work request, data and metadata SG tables, selected queue, MR, and signature-MR flag.
- Queue setup uses `nvme_rdma_alloc_queue`, `nvme_rdma_create_queue_ib`, `nvme_rdma_create_cq`, `nvme_rdma_create_qp`, `nvme_rdma_start_queue`, and `nvme_rdma_conn_established`.
- Controller setup uses `nvme_rdma_alloc_ctrl`, `nvme_rdma_create_ctrl`, `nvme_rdma_setup_ctrl`, `nvme_rdma_configure_admin_queue`, and `nvme_rdma_configure_io_queues`.
- Request path uses `nvme_rdma_queue_rq`, `nvme_rdma_map_data`, `nvme_rdma_dma_map_req`, `nvme_rdma_map_sg_inline`, `nvme_rdma_map_sg_single`, `nvme_rdma_map_sg_fr`, `nvme_rdma_map_sg_pi`, `nvme_rdma_post_send`, and `nvme_rdma_post_recv`.
- Completion and recovery use `nvme_rdma_recv_done`, `nvme_rdma_process_nvme_rsp`, `nvme_rdma_send_done`, `nvme_rdma_inv_rkey_done`, `nvme_rdma_end_request`, `nvme_rdma_complete_rq`, `nvme_rdma_error_recovery`, and reconnect work functions.
- Registration surfaces are `nvme_rdma_transport`, `nvme_rdma_ib_client`, `nvme_rdma_ctrl_ops`, `nvme_rdma_mq_ops`, and `nvme_rdma_admin_mq_ops`.

## Control flow

Module initialization registers an RDMA IB client and then the NVMe fabrics transport. A user-space fabrics connect request calls `nvme_rdma_create_ctrl`, which allocates a controller, fills defaults such as RDMA port, parses remote and optional local addresses, rejects duplicate connects unless allowed, initializes reconnect/error/reset work, allocates queue array storage, initializes the generic NVMe controller, adds it to the core, marks it `CONNECTING`, and calls `nvme_rdma_setup_ctrl`.

Admin setup allocates queue zero, performs RDMA CM address and route resolution, creates CQ/QP/MR pools and response ring, connects the admin queue through `nvmf_connect_admin_queue`, enables the controller, sets max segment and integrity limits from RDMA capabilities, unquiesces the admin queue, and finishes NVMe core initialization. I/O setup asks the controller for an I/O queue count, maps fabrics read/write/poll queue counts, allocates queues, creates the I/O tag set on first setup, starts connect commands for queues, and updates blk-mq hardware queue counts on reconnect.

RDMA connection flow is event-driven by `nvme_rdma_cm_handler`. `ADDR_RESOLVED` creates RDMA resources and starts route resolution. `ROUTE_RESOLVED` sends an RDMA connect request with NVMe RDMA private data describing queue ID, host receive queue size, host submission queue size, and controller ID for I/O queues. `ESTABLISHED` posts all response receives and completes queue setup. Rejection and route/connect/address failures set `cm_error` and release the waiter.

Request submission maps the command capsule for DMA, asks the NVMe core to fill the command, starts the request, decides whether signature MR is needed for T10 PI, maps payload data, and posts a send. Payload mapping always sets NVMe SGL mode. Empty payloads get a null keyed SGL. Small write payloads may be sent inline when the target supports inline data and the capsule has room. A single mapped segment may use an unsafe global rkey only when the module is configured with `register_always=false`; otherwise fast registration is used. PI requests use an integrity MR and signature attributes to let the HCA generate or verify protection information.

Completions are split between receive and send work completions. A receive completion validates length, syncs the response CQE for CPU, special-cases async events, finds the blk-mq request by command ID, stores NVMe status/result, handles remote invalidation if present, optionally posts local invalidation for registered MRs, and then decrements the request refcount. A send completion also decrements the refcount. Only when both sides complete does `nvme_rdma_complete_rq` unmap data, check PI status if needed, unmap the command capsule, and call `nvme_complete_rq`.

Error recovery transitions a live controller to `RESETTING`, queues recovery work, tears down I/O and admin queues without removing tag sets, stops authentication and keep-alive, marks the controller `CONNECTING`, and either schedules reconnect based on fabrics policy or deletes the controller. Reset work follows a similar shutdown and setup path. RDMA device removal finds controllers using that IB device and deletes them.

## State and persistence behavior

Controller state follows the generic NVMe state machine: `NEW`, `CONNECTING`, `LIVE`, `RESETTING`, deletion states, and reconnect counters. RDMA queue flags distinguish allocation, live connection, and transport-resource readiness. CM setup state is communicated through `cm_error` and `cm_done`.

Memory registrations and response rings are queue-lifetime state. MR pools are created per QP and destroyed with the queue. Request-specific MRs are borrowed from pools, invalidated or returned on completion, and cleared before unmapping. The async event SQE is bound to admin queue lifetime. The shared RDMA device list is reference-counted and protected by `device_list_mutex`; controller list state is protected by `nvme_rdma_ctrl_mutex`.

There is no disk persistence in this file. The durable state is remote controller/session state managed through fabrics connect/disconnect, keep-alive, authentication, and reconnection policy. Module parameter `register_always` is read-only after load and affects whether global rkey use is allowed.

## Dependencies and integration points

This transport depends on the NVMe core, NVMe fabrics helpers, blk-mq, blk-integrity, RDMA CM, IB verbs, MR pool helpers, scatterlist DMA mapping, socket address parsing, and optional authentication/TLS-related core behavior through generic controller hooks.

The main integration contracts are `nvmf_transport_ops` for user-requested fabrics controllers, `nvme_ctrl_ops` for core register and lifecycle hooks, blk-mq ops for request handling, `ib_client` for RDMA device removal, and RDMA CM private data defined by NVMe/RDMA. The file also integrates with the core queue mapping helper `nvmf_map_queues` and with authentication cleanup via `nvme_auth_stop`.

## Risks and edge cases

- RDMA connection setup is asynchronous; CM event ordering, route failures, and object teardown must not race with queue destruction.
- Request completion relies on a two-completion refcount plus optional local invalidation. Missing an end path can hang requests; double completion can corrupt blk-mq state.
- Fast registration and invalidation are security-sensitive because stale rkeys could expose host memory. The `register_always=false` global-rkey path is explicitly unsafe and should be tested only in controlled environments.
- PI/signature MR handling modifies command control bits when hardware generates or verifies PI. Incorrect signature attributes can produce silent data-integrity failures or false NVMe PI errors.
- Reconnect can return with changed queue counts; tag-set updates and queue start ranges must match available controller queues.
- Error handling must distinguish live failures, setup failures, and deletion races. Several paths intentionally tolerate state-change failures only when deletion is already in progress.
- The controller duplicate-detection tuple must match fabrics semantics; false negatives create duplicate sessions, while false positives reject valid connections.

## Test signals

Validate connect/disconnect to an NVMe/RDMA target, admin queue setup, I/O queue counts, read/write workloads, queue polling, write/read queue mapping, reconnect after target restart, RDMA device removal, timeout-induced recovery, async events, no-payload admin commands, inline write payloads, fast registration, remote invalidation, local invalidation fallback, PI read/write with guard/reference/application tag failures, and duplicate connect rejection. Fault injection around RDMA CM failures, MR pool exhaustion, DMA map failures, post-send/post-recv failures, and reconnect queue-count changes is especially valuable.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/nvme/host/sysfs.c

## Purpose

`sysfs.c` defines the NVMe core sysfs interface for controllers, namespaces, namespace heads, multipath attributes, optional authentication/TLS attributes, and subsystems. It exposes read-only identity and state attributes, writable control knobs for reset/rescan/delete and fabrics timeout settings, passthrough error logging toggles, DH-HMAC-CHAP secret updates, and TCP TLS key status where configured. It exports attribute groups used by transports such as PCIe and RDMA.

## Important APIs, types, and functions

- Controller control attributes: `reset_controller`, `rescan_controller`, and `delete_controller`.
- Controller identity/state attributes: `model`, `serial`, `firmware_rev`, `cntlid`, `transport`, `subsysnqn`, `address`, `state`, `numa_node`, `queue_count`, `sqsize`, `hostnqn`, `hostid`, `kato`, `cntrltype`, `dctype`, and `quirks`.
- Fabrics timeout attributes: `ctrl_loss_tmo`, `reconnect_delay`, and `fast_io_fail_tmo`.
- Namespace attributes: `wwid`, `uuid`, `nguid`, `eui`, `csi`, `nsid`, `metadata_bytes`, `nuse`, and `passthru_err_log_enabled`; multipath builds add ANA and queue-depth related attributes from other compilation units.
- `dev_to_ns_head` abstracts namespace-head versus per-path disk access.
- `ns_head_update_nuse`, `ns_update_nuse`, and `nuse_show` rate-limit Identify Namespace commands before exposing current namespace utilization.
- Attribute visibility callbacks are `nvme_ns_attrs_are_visible`, `nvme_dev_attrs_are_visible`, `nvme_tls_attrs_are_visible`, and multipath group visibility helpers.
- Authentication handlers are `nvme_ctrl_dhchap_secret_store` and `nvme_ctrl_dhchap_ctrl_secret_store` under `CONFIG_NVME_HOST_AUTH`.
- TCP TLS handlers are `tls_key_show`, `tls_configured_key_show`, `tls_configured_key_store`, `tls_keyring_show`, and `tls_mode_show` under `CONFIG_NVME_TCP_TLS`.
- Exported groups include `nvme_ns_attr_groups`, `nvme_dev_attrs_group`, `nvme_dev_attr_groups`, and `nvme_subsys_attrs_groups`.

## Control flow

Sysfs show/store callbacks start from a `struct device`, recover the relevant `nvme_ctrl`, `nvme_ns`, `nvme_ns_head`, or `nvme_subsystem`, and use `sysfs_emit` for output. Reset calls `nvme_reset_ctrl_sync`, rescan queues a namespace scan, and delete uses `device_remove_file_self` before invoking transport `delete_ctrl` through `nvme_delete_ctrl_sync`. The delete attribute is hidden unless the transport provides a delete operation.

Namespace identity output prefers globally stable identifiers. `wwid_show` emits UUID when present, then NGUID, then EUI64, and finally a legacy vendor/serial/model/nsid string with trailing blanks removed. `uuid_show` preserves backward compatibility by exposing NGUID as UUID if no UUID exists, with a one-time warning. Visibility hides UUID/NGUID/EUI attributes when the underlying identifier is absent.

`nuse_show` updates `head->nuse` through an Identify Namespace command unless rate-limited. For multipath namespace-head disks, it selects an active path under SRCU; for per-path namespaces it queries the concrete namespace controller. The value is then emitted from namespace-head state.

Controller fabrics timeout stores parse integer input and update `ctrl->opts` fields directly. Negative `ctrl_loss_tmo` or `fast_io_fail_tmo` maps to "off"; `ctrl_loss_tmo` converts seconds into `max_reconnects` using the current reconnect delay. These attributes are visible only when `ctrl->opts` exists.

Authentication store paths validate DHCHAP secret syntax, allocate a replacement string, stop current authentication, parse the new key, swap key pointers under `dhchap_auth_mutex`, free old key material, and queue re-authentication work. TLS configured-key store only accepts `0`, negotiates a new key for concat mode, waits for auth completion, and resets the controller so the TLS connection is recreated.

## State and persistence behavior

Most attributes expose live kernel state stored in `nvme_ctrl`, `nvmf_ctrl_options`, `nvme_ns_head`, and `nvme_subsystem`. Writable attributes mutate in-memory controller options and flags. Reset, rescan, delete, re-authentication, and TLS key regeneration trigger asynchronous or synchronous controller behavior beyond sysfs state.

`passthru_err_log_enabled` is a per-controller or per-namespace-head boolean. `ctrl_loss_tmo`, `reconnect_delay`, and `fast_io_fail_tmo` mutate fabrics option fields and affect later recovery behavior. DHCHAP secret updates replace dynamically allocated option strings and parsed key objects; old key objects are freed. TLS attributes expose kernel key serials and configured keyring descriptions without persisting secrets in this file.

`nuse` is cached on the namespace head and refreshed opportunistically with rate limiting. Subsystem identity strings and subtype are owned by the NVMe subsystem object, not by sysfs.

## Dependencies and integration points

The file depends on NVMe core types and helpers from `nvme.h`, fabrics options from `fabrics.h`, Linux sysfs/device/gendisk conventions, optional multipath symbols, optional `linux/nvme-auth.h` support, keyring objects for TLS, and core workqueues such as `nvme_wq`.

Transport drivers consume these groups through `nvme_ctrl_ops.dev_attr_groups` or by composing `nvme_dev_attrs_group` with transport-specific groups. Namespace block devices use `nvme_ns_attr_groups`, and subsystem devices use `nvme_subsys_attrs_groups`. The file also integrates with controller operations such as `get_address`, `delete_ctrl`, reset, scan, Identify Namespace, authentication negotiation, and controller reset.

## Risks and edge cases

- Store callbacks directly change recovery/authentication settings; invalid parsing or missing visibility checks can expose attributes for controllers that do not support them.
- DHCHAP stores echo configured secrets through read attributes. This matches the file behavior but is sensitive from an operational perspective.
- Updating DHCHAP keys requires careful ordering: stop auth, parse new key, swap under mutex, free old key, and queue re-authentication. Errors must leave the previous valid secret intact.
- `nuse_show` issues Identify commands from a read path and can fail with path errors; rate limiting prevents excessive admin commands but may expose stale usage.
- Multipath visibility must hide per-path-only attributes on namespace heads and hide namespace-head-only attributes on paths.
- TLS key regeneration resets the controller; failed negotiation or wait also triggers reset, so userspace writes can be disruptive.
- WWID fallback depends on trimmed serial/model bytes and namespace ID. Devices with bogus identifiers may still produce unstable legacy IDs.

## Test signals

Validate sysfs file presence and permissions for PCIe, RDMA, TCP, discovery, admin, multipath, and non-multipath controllers. Exercise reset, rescan, delete, timeout stores, passthrough logging toggles, namespace identifier visibility, `nuse` refresh and rate limiting, DHCHAP secret replacement and re-authentication, TLS concat key regeneration, TLS visibility gates, subsystem identity attributes, and transport-specific hiding of address/delete/host fields. Negative tests should cover malformed booleans, integers, DHCHAP prefixes, unsupported TLS writes, absent identifiers, and no-path multipath namespace-head reads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/nvme/host/sysfs.c -->
