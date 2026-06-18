# Research: subset-b-005224

This grouped report covers the AACRAID SCSI driver files in `sources/distributed-fs/ceph-client/drivers/scsi/aacraid/`. Each section is source-path aligned for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aachba.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aachba.c

## Purpose

`aachba.c` is the high-level SCSI command and storage-management path for the AACRAID driver. It translates Linux SCSI mid-layer commands into AAC firmware FIBs for logical containers, SRB passthrough commands for non-DASD/JBOD devices, and native HBA commands for newer SA/SRC firmware. It also discovers logical containers, maintains per-container geometry and sense state, emulates common SCSI commands locally, and exposes a small set of container-oriented ioctls used by the broader management path.

The file is central to runtime I/O. It sits above the adapter-specific transport in `a_ops` and below the SCSI host template callbacks. It depends on data structures, firmware command IDs, feature flags, and helper prototypes from `aacraid.h`.

## Important APIs, Types, and Functions

Important exported or externally referenced functions:

- `aac_get_config_status(struct aac_dev *dev, int commit_flag)`: queries firmware configuration status and optionally sends `CT_COMMIT_CONFIG`.
- `aac_get_containers(struct aac_dev *dev)`: allocates/resizes `dev->fsa_dev` and probes all container IDs.
- `aac_probe_container(struct aac_dev *dev, int cid)`: builds a temporary `scsi_cmnd` and synchronously probes a single container.
- `aac_setup_safw_adapter(struct aac_dev *dev)`: populates logical containers and SA firmware physical-device topology.
- `aac_get_adapter_info(struct aac_dev *dev)`: fetches firmware adapter and supplemental information, configures flags and adapter operation callbacks.
- `aac_scsi_cmd(struct scsi_cmnd *scsicmd)`: main SCSI command dispatcher for logical arrays, controller pseudo-device, non-DASD passthrough, and native HBA devices.
- `aac_dev_ioctl(struct aac_dev *dev, unsigned int cmd, void __user *arg)`: handles container query/delete/get-container ioctls before the generic control layer.
- `aac_hba_callback(void *context, struct fib *fibptr)`: completion callback for native HBA commands.
- `get_container_type(unsigned type)`: maps container type codes to display strings.

Important internal helpers:

- Container discovery: `_aac_probe_container()`, `_aac_probe_container1()`, `_aac_probe_container2()`, `aac_probe_container_callback1/2()`.
- Inquiry metadata: `setinqstr()`, `setinqserial()`, `aac_get_container_name()`, `aac_get_container_serial()`, `build_vpd83_type3()`.
- Logical volume I/O: `aac_read()`, `aac_write()`, `aac_read_raw_io()`, `aac_write_raw_io()`, `aac_read_block()`, `aac_write_block()`, `aac_read_block64()`, `aac_write_block64()`.
- Passthrough and HBA: `aac_scsi_common()`, `aac_scsi_32()`, `aac_scsi_64()`, `aac_adapter_hba()`, `aac_send_srb_fib()`, `aac_send_hba_fib()`.
- Completion mapping: `io_callback()`, `aac_srb_callback()`, `hba_resp_task_complete()`, `hba_resp_task_failure()`.
- Scatter-gather construction: `aac_build_sg()`, `aac_build_sg64()`, `aac_build_sgraw()`, `aac_build_sgraw2()`, `aac_convert_sgraw2()`, `aac_build_sghba()`.
- Cache and power management: `aac_synchronize()`, `synchronize_callback()`, `aac_start_stop()`, `aac_start_stop_callback()`.
- SA firmware topology: `aac_get_safw_ciss_luns()`, `aac_issue_safw_bmic_identify()`, `aac_set_safw_attr_all_targets()`, cleanup helpers for CISS data.

Local types include SCSI inquiry and VPD layouts (`struct inquiry_data`, `struct tvpd_page83`, descriptor structs) plus packed MODE SENSE response layouts. These are copied directly into SCSI scatterlists with `scsi_sg_copy_from_buffer()`.

Module parameters define runtime policy: non-DASD scanning, cache/FUA behavior, DAC mode, config commit behavior, MSI mode, startup/AIF timeouts, FIB dump, ACB counts/sizes, health-check intervals, physical exposure, reset-on-init, and WWN selection.

## Control Flow

Initialization and discovery start with `aac_get_adapter_info()`. It sends `RequestAdapterInfo`, optionally sends `RequestSupplementAdapterInfo`, fetches bus information, resets `hba_map`, prints firmware metadata, derives flags such as `nondasd_support`, `jbod`, `raid_scsi_mode`, `dac_support`, and selects function pointers in `dev->a_ops` for reads, writes, bounds checks, and SCSI passthrough. Raw I/O controllers use `ContainerRawIo` or `ContainerRawIo2`; older controllers use container block read/write FIBs; DAC-capable controllers can use 64-bit SG commands.

Logical volume discovery is layered. `aac_get_containers()` queries `CT_GET_CONTAINER_COUNT`, ensures `dev->fsa_dev` is large enough, clears entries, then calls `aac_probe_container()` for each container. `aac_probe_container()` synthesizes a temporary SCSI command and waits until the asynchronous FIB callback clears the device pointer. `_aac_probe_container()` first issues `VM_NameServe` or `VM_NameServeAllBlk`; `_aac_probe_container1()` falls back to `VM_NameServe64` when needed; `_aac_probe_container2()` validates mount data, fills `fsa_dev_info` with block size, capacity, type, read-only state, identifier, validity, and sense readiness.

At runtime `aac_scsi_cmd()` is the main dispatcher. It validates container channel, target ID, and LUN. If a container is missing or not ready, selected commands such as INQUIRY, TEST UNIT READY, READ CAPACITY, and READ CAPACITY(16) trigger reprobe. Native physical devices on non-container channels are sent to `aac_send_hba_fib()` when `hba_map` says `AAC_DEVTYPE_NATIVE_RAW`; other exposed physical/JBOD/non-DASD devices go through `aac_send_srb_fib()`. Controller pseudo-device commands are limited to INQUIRY and TEST UNIT_READY.

For logical arrays, `aac_scsi_cmd()` handles reads and writes by parsing the CDB LBA and transfer length, checking against `fsa_dev[cid].size`, applying adapter bounds checks, allocating a tagged FIB, and calling the selected adapter read/write function. It emulates or services INQUIRY, VPD pages 0, 0x80, and 0x83, READ CAPACITY(10/16), MODE SENSE(6/10), REQUEST SENSE, ALLOW MEDIUM REMOVAL, TEST UNIT READY, no-op legacy commands, SYNCHRONIZE CACHE, and START STOP. Unknown commands return CHECK CONDITION with illegal-request sense data.

Completions map firmware status into Linux SCSI results. `io_callback()` handles container I/O status, unmaps DMA, updates per-container sense data, completes the FIB, and finishes the SCSI command. `aac_srb_callback()` maps SRB status and SCSI status from firmware for passthrough devices and copies autosense data. `aac_hba_callback()` maps native HBA service responses, handles task management completions specially, and avoids DMA unmap for native HBA TMF commands.

## State and Persistence Behavior

The file does not persist data to disk, but it maintains driver and firmware-derived state across I/O:

- `dev->fsa_dev` is the primary logical-container table. Each `struct fsa_dev_info` stores validity, size, block size, type, read-only flag, lock/delete flags, name, sense data, and VPD identifier.
- `dev->hba_map[bus][target]` records physical-device mode for SA/SRC firmware, including native raw vs ARC raw vs RAID member, queue-depth limits, scan counters, and firmware nexus values.
- `dev->adapter_info` and `dev->supplement_adapter_info` are refreshed from firmware and drive feature flags, limits, and display strings.
- `dev->cache_protected`, `dev->nondasd_support`, `dev->raid_scsi_mode`, `dev->dac_support`, `dev->needs_dac`, `dev->jbod`, `dev->raw_io_interface`, and `dev->raw_io_64` control I/O paths.
- Per-command ownership is tracked through `aac_priv(scsicmd)->owner`, which distinguishes firmware-owned commands from mid-layer-owned commands and is used by shutdown/drain logic elsewhere.
- Module parameters are global driver policy knobs and can materially affect device exposure and cache semantics.

Sense data is stateful. Several paths write `dev->fsa_dev[cid].sense_data`, and REQUEST SENSE copies then clears it. This means stale or incorrectly updated sense state can alter later SCSI behavior.

## Dependencies and Integration Points

This file depends heavily on Linux SCSI APIs (`struct scsi_cmnd`, `scsi_done`, `scsi_dma_map/unmap`, `scsi_sg_copy_*`, `scsi_set_resid`), PCI/DMA APIs, byte-order helpers, and AAC firmware ABIs in `aacraid.h`. It integrates with the FIB allocator and transport in other AACRAID files through `aac_fib_alloc[_tag]()`, `aac_fib_init()`, `aac_fib_send()`, `aac_hba_send()`, `aac_fib_complete()`, `aac_fib_free()`, and adapter operation macros such as `aac_adapter_read()` and `aac_adapter_scsi()`.

It also integrates with management tooling through `aac_dev_ioctl()`, which is called first from `aac_do_ioctl()` in `commctrl.c`. Container state discovered here is reported to user space by query/delete ioctls and by SCSI inquiry/capacity commands.

## Risks and Edge Cases

- The SCSI dispatch path has many feature-dependent branches. Regressions in `aac_get_adapter_info()` callback selection can silently route I/O through the wrong firmware ABI.
- `aac_build_sghba()` appears to adjust the final SGE length using `le32_to_cpu(sge->len) - byte_count - scsi_bufflen(scsicmd)`. Other SG builders subtract `(byte_count - scsi_bufflen)`. This deserves focused review because an arithmetic sign error would corrupt native HBA SGL lengths when DMA mapping exceeds the requested transfer length.
- Several asynchronous paths rely on valid `scsi_cmnd` context and `aac_valid_context()` to avoid completing corrupt commands. Lifetime assumptions around probe-time synthetic commands are delicate.
- Raw I/O and SG conversion must honor firmware limits. `aac_build_sgraw2()` can rewrite non-conformant SGLs if `aac_convert_sgl` is enabled; failures or disabled conversion can expose firmware-specific SG constraints.
- Cache policy is controlled by the `aac_cache` bitmask and battery/cache protection state. Misconfiguration can change FUA and SYNCHRONIZE CACHE semantics.
- VPD and INQUIRY emulation depends on `fsa_dev` state and firmware serial queries. Array migration notes around fake serials indicate identity stability is historically sensitive.
- Device exposure knobs (`nondasd`, `expose_physicals`, `jbod`) can change what the SCSI mid-layer sees and should be tested with hidden RAID members, JBODs, and native HBA devices.
- Container probing uses `schedule()` polling on a synthetic command. Dead callbacks or reset races can hang discovery loops.
- The file mixes synchronous firmware requests, asynchronous callbacks, DMA mapping, and SCSI completion, so reset and shutdown races are high-risk.

## Test Signals

Useful validation signals include boot/probe logs for adapter, kernel, monitor, BIOS, serial, non-DASD, DAC, and RAID/SCSI mode; successful `aac_get_containers()` population; SCSI scan results for container channel and native/JBOD channels; INQUIRY and VPD 0/0x80/0x83 output; READ CAPACITY(10/16) for small and >2 TiB arrays; MODE SENSE WCE/FUA behavior; read/write I/O through raw, block, 32-bit, 64-bit, and native HBA paths; SYNCHRONIZE CACHE and START STOP behavior; passthrough SRB status mapping; request-sense clearing; reset and shutdown while I/O is active; and fault injection for ST_NOT_READY, ST_MEDERR, SRB timeout/no-device/busy, native HBA failure statuses, and illegal LBA handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aachba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aacraid.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aacraid.h

## Purpose

`aacraid.h` is the shared ABI and state-definition header for the AACRAID driver. It defines the firmware command numbers, queue layouts, FIB headers, adapter initialization records, scatter-gather formats, SCSI/SRB/HBA command and response formats, ioctl request numbers, adapter state structures, feature flags, register mappings, helper macros, inline helpers, and cross-file function prototypes used by the driver implementation.

This header is not a passive declaration file. It encodes firmware contracts that must match controller expectations, including packed/native command layout, endianness, queue ordering, init-structure revisions, and status codes. Changes here can affect every transport, SCSI, ioctl, reset, interrupt, and discovery path.

## Important APIs, Types, and Definitions

Major constants and feature definitions:

- Interrupt and mode flags: `AAC_INT_MODE_*`, `AAC_ENABLE_*`, `AAC_DISABLE_*`, PMC interrupt bits, doorbell bits.
- Capacity and topology limits: `MAXIMUM_NUM_CONTAINERS`, `AAC_NUM_MGT_FIB`, `AAC_NUM_IO_FIB`, `AAC_MAX_LUN`, `AAC_MAX_BUSES`, `AAC_MAX_TARGETS`, `AAC_MAX_NATIVE_SIZE`, `AAC_MAX_MSIX`.
- Firmware options and extended options: `AAC_OPT_*`, `AAC_EXTOPT_*`, `AAC_OPTION_*`, `AAC_FEATURE_JBOD`.
- Communication interface types: `AAC_COMM_PRODUCER`, `AAC_COMM_MESSAGE`, and message type 1/2/3.
- FIB commands: `ContainerCommand`, `ContainerCommand64`, `ContainerRawIo`, `ContainerRawIo2`, `ScsiPortCommand`, `ScsiPortCommand64`, `RequestAdapterInfo`, `RequestSupplementAdapterInfo`, `AifRequest`, and others.
- Container manager commands: `CT_GET_CONFIG_STATUS`, `CT_COMMIT_CONFIG`, `CT_GET_CONTAINER_COUNT`, `CT_READ_NAME`, `CT_CID_TO_32BITS_UID`, `CT_FLUSH_CACHE`, `CT_POWER_MANAGEMENT`, `CT_PAUSE_IO`, `CT_RELEASE_IO`.
- User ioctl command numbers: `FSACTL_SENDFIB`, `FSACTL_SEND_RAW_SRB`, `FSACTL_QUERY_DISK`, `FSACTL_DELETE_DISK`, `FSACTL_OPEN_GET_ADAPTER_FIB`, `FSACTL_GET_NEXT_ADAPTER_FIB`, `FSACTL_RESET_IOP`, `FSACTL_GET_HBA_INFO`.

Core data structures:

- `struct aac_dev`: main per-adapter state. It stores negotiated limits, FIB memory, queues, locks, adapter operation callbacks, PCI/register mappings, SCSI host pointer, container table, AIF context list, firmware info blocks, capability flags, sync state, MSI/MSI-X state, HBA target map, SA firmware CISS data, and shutdown/reset flags.
- `struct adapter_ops`: polymorphic adapter hooks for interrupts, sync commands, restart/start, ioremap, FIB delivery, bounds/read/write/SCSI paths, and communication selection.
- `struct fib`, `struct hw_fib`, `struct aac_fibhdr`, `struct aac_fib_xporthdr`: host and firmware FIB representations.
- `struct aac_queue`, `struct aac_queue_block`, `struct aac_entry`, `struct aac_qhdr`: producer/consumer queue infrastructure shared with firmware.
- `union aac_init`: adapter init structures for older r7-style interfaces and newer r8/type3 RRQ interfaces.
- `struct fsa_dev_info`: per-logical-container state consumed by SCSI command handling.
- `struct aac_hba_map_info`, `struct aac_hba_cmd_req`, `struct aac_hba_resp`, `struct aac_native_hba`: native HBA request/response state and physical target mapping.
- `struct aac_srb`, `struct aac_srb_reply`, `struct user_aac_srb`: firmware SCSI passthrough command ABI and user-space representation.
- `struct aac_adapter_info`, `struct aac_supplement_adapter_info`, `struct aac_bus_info_response`, `struct aac_hba_info`: firmware and management metadata.
- `struct aac_fib_context`: user AIF subscription context for adapter-initiated FIB delivery.

Important inline helpers and macros:

- Adapter operation macros such as `aac_adapter_read()`, `aac_adapter_write()`, `aac_adapter_scsi()`, `aac_adapter_sync_cmd()`, and `aac_adapter_check_health()`.
- `fib_data(fibctx)` to access FIB payload data.
- `aac_priv(struct scsi_cmnd *cmd)` to get AAC per-command private state.
- `aac_is_src()` and `aac_supports_2T()` feature helpers.
- Worker scheduling helpers for SA firmware scans and SRC AIF reinitialization.

## Control Flow and Design Role

The header defines the driver layering. Adapter-specific files fill `struct adapter_ops`; initialization code negotiates communication settings and fills `struct aac_dev`; SCSI code uses operation macros to call the selected transport; ioctl code uses the same FIB ABI to pass control commands between user space and firmware.

FIB flow is described by the `struct aac_fibhdr` fields and `enum fib_xfer_state`. Host-owned/adapter-owned state, response expectation, priority, async state, fast response, and API-FIB markers are all encoded in the header. Transport code builds queue entries from `struct aac_entry`, while higher-level code fills payload structs such as `struct aac_read`, `struct aac_write`, `struct aac_raw_io2`, or `struct aac_srb`.

Initialization flow is driven by `union aac_init`. Older communication modes use r7 fields for adapter FIBs, communication queue headers, printf buffer, host memory pages, max I/O commands, max FIB size, and host RRQ addresses. Type3/SA firmware uses r8 fields with multiple host RRQs and MSI-X vector metadata. `comminit.c` fills these layouts according to the negotiated interface.

## State and Persistence Behavior

No data is persisted to disk by this header, but it defines all important in-memory state and firmware-visible DMA layout. The state lifetime is typically per-adapter:

- DMA coherent regions are tracked through `comm_addr`, `comm_phys`, `init`, `host_rrq`, `hw_fib_va`, `hw_fib_pa`, and related fields.
- Logical containers persist in memory through `fsa_dev` until rescan/reset/free.
- Physical target exposure persists through `hba_map`.
- User-space AIF consumers persist through `fib_list` entries of `struct aac_fib_context`.
- Reset/shutdown state is tracked in `adapter_shutdown`, `in_reset`, `in_soft_reset`, `handle_pci_error`, and `init_reset`.
- Module-global policy variables are declared here and defined elsewhere, allowing runtime parameters to influence all files.

Because these structures are firmware ABI, state layout itself is a persistence boundary across firmware/driver versions. Endianness annotations (`__le32`, `__le16`, `__le64`) mark values that cross that boundary.

## Dependencies and Integration Points

`aacraid.h` depends on Linux interrupt, completion, PCI, and SCSI host/command headers. It is included by the major driver source files. It exposes prototypes for FIB allocation/delivery, adapter initialization, SCSI command handling, ioctl handling, reset, IRQ setup, scanning, AIF handling, and adapter-specific init routines.

Integration with the Linux SCSI mid-layer occurs through `struct Scsi_Host`, `struct scsi_cmnd`, command-private data, host wait queues, and delayed-work scan helpers. Integration with PCI and DMA occurs through register mapping structs and DMA address fields. Integration with user space occurs through ioctl constants and user-visible structures.

## Risks and Edge Cases

- Firmware ABI structures must retain exact field order, size, alignment, and endianness. Even small layout changes can break controller communication.
- Several flexible arrays and variable-size structures (`sg[]`, `rrq[]`, CISS LUN list) require careful size calculations in callers.
- `struct aac_dev` is broad shared mutable state. Locking rules are distributed across source files, increasing the risk of reset, ioctl, AIF, and SCSI races.
- The header includes both firmware-endian and CPU-endian user structures. Confusing `struct aac_srb` with `struct user_aac_srb` can introduce endian or pointer bugs.
- FIB state flags are bitfields shared by transport and high-level code. Incorrect flags can cause double completion, missing response waits, or leaked FIBs.
- Feature flags such as native HBA, new communication modes, SA firmware, 64-bit SG, and variable block size alter control flow in multiple files. Test coverage must combine these flags, not validate them in isolation.
- Register definitions for SA, RX, RKT, and SRC devices are hardware-specific and accessed through macros, so wrong adapter identification can produce invalid MMIO.

## Test Signals

Useful signals include successful build-time size/alignment assumptions for firmware ABI structs, probe logs showing negotiated communication interface and init revision, correct queue and RRQ setup for producer/message/type1/type2/type3 modes, SCSI scan behavior across container and native channels, ioctl compatibility for 32-bit and 64-bit user space, reset behavior with `adapter_shutdown` and `handle_pci_error`, MSI/MSI-X interrupt routing, AIF delivery to user contexts, and DMA/FIB leak checks under I/O, passthrough, reset, and shutdown stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/aacraid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/commctrl.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/commctrl.c

## Purpose

`commctrl.c` implements the AACRAID management ioctl control path. It lets privileged management tools send raw FIBs or raw SRBs to firmware, subscribe to adapter-initiated FIB events, query driver/PCI/HBA metadata, and request adapter reset. It also delegates container-level ioctls to `aac_dev_ioctl()` in `aachba.c` before handling broader communication-layer commands.

This file is the highest-risk user/kernel boundary in the group. It copies user-controlled structures, validates sizes and SG counts, allocates bounce buffers, maps DMA, sends firmware commands, returns firmware replies, and maintains per-user AIF contexts.

## Important APIs, Types, and Functions

Externally visible function:

- `aac_do_ioctl(struct aac_dev *dev, unsigned int cmd, void __user *arg)`: central ioctl dispatcher, serialized by `dev->ioctl_mutex`.

Important internal functions:

- `ioctl_send_fib()`: copies a user FIB, validates header and sender sizes, optionally allocates a larger coherent FIB for up to 2048-byte requests, sends it synchronously, completes it, and copies the reply back.
- `open_getadapter_fib()`: creates an `aac_fib_context`, assigns a unique 32-bit handle, initializes its completion/list state, and links it into `dev->fib_list`.
- `next_getadapter_fib()`: validates a user context handle, optionally waits for an AIF FIB, copies the next queued adapter FIB to user space, frees the queued copy, and restarts the AIF thread if needed.
- `aac_close_fib_context()` and `close_getadapter_fib()`: free queued FIBs and remove a user AIF context.
- `check_revision()`: reports driver compatibility version/build.
- `aac_send_raw_srb()`: sends a user-provided SCSI request either as legacy SRB passthrough or native HBA command, including user SG copy, DMA mapping, firmware command issue, data copy-back, and reply construction.
- `aac_get_pci_info()` and `aac_get_hba_info()`: copy basic adapter metadata to user space.
- `aac_send_reset_adapter()`: marks adapter shutdown and invokes `aac_reset_adapter()` outside the ioctl mutex.

Local structs include `compat_fib_ioctl`, `aac_pci_info`, and `aac_reset_iop`.

## Control Flow

`aac_do_ioctl()` locks `dev->ioctl_mutex`, rejects commands when `adapter_shutdown` is already set, gives `aac_dev_ioctl()` first chance to handle container-specific requests, and then switches on `FSACTL_*` commands. It unlocks in all exit paths.

`ioctl_send_fib()` allocates a driver FIB, copies the user FIB header first, computes the effective copy size from header `Size` and `SenderSize`, enforces `dev->max_fib_size` or a hard 2048-byte upper bound, and if needed temporarily swaps `fibptr->hw_fib_va` to a larger coherent allocation. `TakeABreakPt` is handled locally by forcing an adapter interrupt. Other commands go through `aac_fib_send()` and `aac_fib_complete()`. The resulting FIB buffer is copied back to user space, and any temporary coherent allocation is released.

The adapter-FIB subscription path starts with `open_getadapter_fib()`, which creates a context and returns an opaque `unique` handle. `next_getadapter_fib()` accepts native and compat ioctl layouts, finds the context under `dev->fib_lock`, returns a queued FIB if one is available, or waits on the context completion if requested. If the AIF thread appears stopped and the adapter is usable, it tries to restart `aac_command_thread()`.

`aac_send_raw_srb()` is the most complex path. It requires `CAP_SYS_ADMIN`, rejects reset state, allocates a FIB, reads the user-provided `count` as the request size, validates it against the expected `user_aac_srb` and SG layout sizes, determines DMA direction from SRB flags, and limits SG count to `HBA_MAX_SG_EMBEDDED`. For native HBA targets identified in `dev->hba_map`, it builds `struct aac_hba_cmd_req`; otherwise it builds an endian-converted `struct aac_srb`. It then allocates kernel bounce buffers for each user SG entry, copies outbound data, maps each buffer for DMA, fills the firmware SG list, sends the command synchronously, copies inbound data back, and copies either an HBA-derived synthetic SRB reply or the firmware SRB reply to user space.

## State and Persistence Behavior

Persistent in-memory state includes:

- `dev->fib_list`, a list of open AIF contexts, protected by `dev->fib_lock`.
- Per-context `fib_list`, `count`, `completion`, `wait`, and `jiffies`, which track queued adapter FIB events and consumer activity.
- `dev->adapter_shutdown`, set by reset ioctl and checked by the dispatcher to block later commands.
- `dev->ioctl_mutex`, serializing ioctl entry points.

The file does not persist state outside memory. User SG buffers are copied into temporary kernel memory and mapped for one command lifetime. Queued AIF FIB copies are heap-allocated and freed when delivered or context-closed.

## Dependencies and Integration Points

This file integrates with user space through `copy_from_user()`, `copy_to_user()`, `memdup_user()`, compat pointer handling, ioctl command constants, and Linux capability checks. It integrates with firmware through `aac_fib_send()`, `aac_hba_send()`, FIB completion/free routines, SRB/HBA structures, and adapter reset. It integrates with event delivery through `aac_command_thread()` and `dev->fib_list`. It calls `aac_dev_ioctl()` for container-specific requests implemented in `aachba.c`.

## Risks and Edge Cases

- `aac_send_raw_srb()` maps DMA buffers with `dma_map_single()` but the visible cleanup path frees `sg_list` buffers without an explicit `dma_unmap_single()`. That deserves focused review against surrounding driver conventions and IOMMU expectations.
- Native-HBA reply copying uses `memcpy(reply.sense_data, err->sense_response_buf, AAC_SENSE_BUFFERSIZE)` while the native sense buffer is `HBA_SENSE_DATA_LEN_MAX`. The current constants are close but not identical; future size changes could create truncation or overflow risk.
- User-provided SG addresses and counts are heavily validated, but this remains a broad privileged attack surface. Boundary tests should cover mixed 32/64-bit SG layouts, zero SG count, oversized count, and invalid copy faults.
- `close_getadapter_fib()` searches `dev->fib_list` before taking `dev->fib_lock`, then locks only for close. Concurrent AIF activity or close/open operations could race.
- `next_getadapter_fib()` returns after dropping the lock and then updates `fibctx->jiffies` outside the protected region, which may be fragile if close races exist.
- `ioctl_send_fib()` trusts firmware-updated FIB contents for copy-back size established before send. Size validation before and after user copy is present, but firmware response size behavior should be tested.
- Reset ioctl intentionally unlocks the ioctl mutex around `aac_reset_adapter()`. That prevents deadlock but allows other state changes during reset; the `adapter_shutdown` flag is the main guard.

## Test Signals

Useful validation includes ioctl fuzzing with invalid sizes and pointers, compat ioctl coverage, CAP_SYS_ADMIN enforcement for raw SRB, successful management FIB send and large-FIB send, AIF open/next/wait/close lifecycle, concurrent AIF consumers, AIF thread restart behavior, raw SRB passthrough on 32-bit and 64-bit SG adapters, native HBA passthrough, DMA mapping fault injection, copy fault injection for inbound/outbound buffers, reset ioctl behavior, and leak/race checks for FIB contexts and SG buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/commctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/comminit.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/comminit.c

## Purpose

`comminit.c` initializes and tears down the host-to-adapter communication interface for AACRAID adapters. It negotiates firmware communication capabilities, allocates the coherent DMA region containing adapter FIB space, host response queues, the adapter init structure, command/response queues, and the firmware printf buffer, initializes queue headers, selects interrupt mode, drains active I/O during shutdown, and sends the firmware close-all request.

This file is the bridge between early adapter-specific probe code and the runtime FIB/SCSI paths. It produces the `struct aac_dev` communication state consumed by `aachba.c`, `commctrl.c`, and lower-level transport files.

## Important APIs, Types, and Functions

Externally visible functions:

- `struct aac_common aac_config`: global communication configuration, defaulting interrupt moderation on.
- `aac_send_shutdown(struct aac_dev *dev)`: drains firmware-owned SCSI commands, sends `VM_CloseAll`, frees the shutdown FIB, and reverts SRC MSI-X adapters to INTx.
- `aac_define_int_mode(struct aac_dev *dev)`: chooses MSI-X vector count and per-vector capacity for SRC adapters.
- `aac_init_adapter(struct aac_dev *dev)`: negotiates firmware capabilities, initializes locks and limits, allocates communication queues and FIBs, and returns initialized adapter state or `NULL`.

Important internal functions:

- `aac_is_msix_mode()` and `aac_change_to_intx()`: detect and force interrupt mode on SRC hardware before initialization.
- `aac_alloc_comm()`: performs the main coherent DMA allocation and fills `dev->init`, `dev->host_rrq`, `dev->comm_addr`, `dev->printfbuf`, and related physical addresses.
- `aac_queue_init()`: initializes one firmware queue's producer/consumer pointers, wait queues, lock, command list, and entry count.
- `wait_for_io_iter()` and `aac_wait_for_io_completion()`: count and wait for SCSI commands still owned by firmware.
- `aac_comm_init()`: lays out and initializes the eight communication queues in the shared communication area.

## Control Flow

`aac_init_adapter()` starts by initializing management and sync locks, defaulting FIB and SG limits for the old 512-byte FIB format, selecting producer communication, and clearing raw I/O flags. If an SRC adapter is already in MSI-X mode, it switches firmware back to INTx before capability negotiation.

It then sends `GET_ADAPTER_PROPERTIES` through `aac_adapter_sync_cmd()`. A successful response can enable newer communication interfaces, raw I/O, 64-bit raw I/O, SA firmware mode, and soft-reset support. If firmware reports a larger mapping requirement for message communication, the function remaps the adapter MMIO footprint and falls back to producer mode on failure.

Next it sends `GET_COMM_PREFERRED_SETTINGS`, which supplies maximum command size, max FIB size, SG limits, outstanding FIB counts, and max AIF count. These values update `host->max_sectors`, `dev->max_fib_size`, `host->sg_tablesize`, `dev->sg_tablesize`, `host->can_queue`, and `dev->max_num_aif`. The `numacb` module parameter can further reduce `host->can_queue`. SRC adapters call `aac_define_int_mode()` to determine MSI-X use and response-queue partitioning.

After negotiation, `aac_init_adapter()` allocates `dev->queues`, calls `aac_comm_init()` to allocate and initialize the coherent communication area, calls `aac_fib_setup()` to initialize the FIB pool, and initializes `dev->fib_list` and `dev->sync_fib_list`.

`aac_alloc_comm()` computes the allocation size based on `max_fib_size`, init-structure revision, queue area size, alignment, printf buffer size, and host RRQ needs. For type1/type2/type3 communication it reserves host RRQ memory. Type3 with SA firmware reserves an r8 init structure with per-vector RRQ descriptors. Older interfaces fill the r7 init structure with adapter FIB physical address, host memory pages, max I/O commands, max I/O size, max FIB size, max AIFs, host RRQ address, and feature flags. It then aligns the queue header region, stores the communication header physical address when applicable, and places the printf buffer after the queues.

`aac_comm_init()` lays out the eight queues in firmware-defined order: host normal/high command, adapter normal/high command, host normal/high response, adapter normal/high response. It also shares locks between opposite-direction queues that must serialize access to the same firmware-facing side.

`aac_send_shutdown()` checks adapter health, sets `adapter_shutdown` under the ioctl mutex, waits up to roughly 60 seconds for firmware-owned SCSI commands to complete, sends a synchronous `VM_CloseAll` container command, completes/frees the FIB, and changes SRC MSI-enabled adapters back to INTx mode.

## State and Persistence Behavior

The file creates and updates key per-adapter runtime state:

- `dev->comm_addr`, `comm_phys`, and `comm_size` track the coherent DMA communication allocation.
- `dev->init` and `init_pa` point at the firmware initialization structure inside that DMA allocation.
- `dev->host_rrq` and `host_rrq_pa` hold response queue memory for newer communication interfaces.
- `dev->printfbuf` points at the firmware printf buffer.
- `dev->queues` holds the software representation of the eight firmware queues.
- `dev->max_fib_size`, `max_num_aif`, `max_cmd_size`, `sg_tablesize`, `comm_interface`, `raw_io_interface`, `raw_io_64`, `sync_mode`, `sa_firmware`, `soft_reset_support`, `max_msix`, `vector_cap`, and `msi_enabled` are negotiated state.
- `dev->adapter_shutdown` is set during shutdown/reset coordination.

The state is volatile and per adapter. It is made firmware-visible through coherent DMA rather than persisted to storage.

## Dependencies and Integration Points

`comminit.c` depends on adapter-specific sync commands and MMIO operations through `aac_adapter_sync_cmd()`, `aac_adapter_ioremap()`, `aac_src_access_devreg()`, and SRC register macros from `aacraid.h`. It depends on Linux DMA coherent allocation, PCI MSI-X allocation, CPU count, SCSI host limits, delayed sleeps, and `scsi_host_busy_iter()`.

It integrates directly with FIB lifecycle setup through `aac_fib_setup()`, shutdown FIB sending through `aac_fib_send()`, and SCSI command ownership through `aac_priv(cmd)->owner`. Its output state is consumed by all runtime FIB senders, including the SCSI paths in `aachba.c` and management ioctls in `commctrl.c`.

## Risks and Edge Cases

- Firmware-reported limits drive allocation sizes and queue depths. Bad negotiation or insufficient validation can cause undersized DMA regions, SG overflows, or queue starvation.
- Type3/SA firmware uses multi-vector host RRQs and a larger r8 init structure. Off-by-one or vector-capacity errors can break completion delivery under MSI-X.
- `aac_alloc_comm()` returns `0` on allocation failure and `1` on success, while callers translate failure to `-ENOMEM`; this convention should stay consistent.
- Interrupt-mode transitions from MSI-X to INTx occur before init and during shutdown for SRC devices. Failure to transition cleanly could strand firmware interrupts.
- `aac_wait_for_io_completion()` only waits for commands whose private owner is `AAC_OWNER_FIRMWARE`. Incorrect owner transitions elsewhere can make shutdown either wait too little or report false outstanding I/O.
- Cleanup on partial `aac_init_adapter()` failure frees `dev->queues` but relies on other teardown paths for DMA/FIB allocations if later stages fail. Failure-injection tests should verify no coherent-memory leak.
- `numacb` can reduce queue depth. Very small or firmware-limited queues need testing for management FIB reservation (`AAC_NUM_MGT_FIB`) interactions.

## Test Signals

Useful signals include probe logs for communication interface type, successful fallback from unsupported message/MMIO sizing to producer mode, valid `host->can_queue`, SG table, max sectors, and max FIB values after negotiation, MSI-X vector allocation and vector-cap partitioning, coherent DMA allocation/free leak checks, queue producer/consumer initialization matching firmware expectations, FIB setup success, shutdown drain logs with active command counts, successful `VM_CloseAll`, INTx fallback after shutdown on SRC MSI adapters, and fault injection for failed sync commands, failed DMA allocation, failed queue allocation, failed FIB setup, and firmware-reported edge limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/comminit.c -->
