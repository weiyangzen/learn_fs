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

At runtime `aac_scsi_cmd()` is the main dispatcher. It validates container channel, target ID, and LUN. If a container is missing or not ready, selected commands such as INQUIRY, TEST UNIT READY, READ CAPACITY, and READ CAPACITY(16) trigger reprobe. Native physical devices on non-container channels are sent to `aac_send_hba_fib()` when `hba_map` says `AAC_DEVTYPE_NATIVE_RAW`; other exposed physical/JBOD/non-DASD devices go through `aac_send_srb_fib()`. Controller pseudo-device commands are limited to INQUIRY and TEST_UNIT_READY.

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
