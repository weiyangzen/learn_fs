# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_main.c

## Purpose

`qed_main.c` is the central core-module glue for the QLogic/Marvell FastLinQ 4xxxx QED driver. It initializes module-level link-mode maps, probes and removes core devices, owns PCI BAR/DMA setup, configures interrupt modes, starts and stops the slowpath, exposes the `qed_common_ops_pass` vtable to protocol drivers, translates link configuration/status between MFW and Linux-facing structures, handles firmware/NVM flashing helpers, schedules recovery and management TLV work, and allocates/deallocates LL2 interface state when protocol personalities need light-L2 support.

The file is not a Linux `pci_driver` registration by itself in this snapshot; instead it exports operations that upper protocol-specific QED clients call through common ops.

## Important APIs, types, and functions

Module initialization:

- `qed_init()` prints the core module version and calls `qed_mfw_speed_maps_init()`.
- `qed_mfw_speed_map_populate()` and `qed_mfw_speed_maps_init()` convert static arrays of ethtool link-mode bit numbers into `link_mode` masks stored in `qed_mfw_ext_maps[]` and `qed_mfw_legacy_maps[]`.
- `MODULE_FIRMWARE(QED_FW_FILE_NAME)` declares the zipped init-values firmware file derived from firmware version macros.

Device lifecycle:

- `qed_alloc_cdev()` allocates and initializes `struct qed_dev`.
- `qed_init_pci()` enables the PCI device, validates BARs, requests regions, sets bus mastering, saves PCI state, checks revision and PCIe capability, sets 64-bit DMA mask, maps BAR0 registers, and maps BAR2 doorbells for PFs.
- `qed_free_pci()` unmaps doorbells/registers, releases regions when appropriate, and disables the PCI device.
- `qed_probe()` allocates `qed_dev`, sets protocol/VF/recovery/debug state, initializes PCI, and calls `qed_hw_prepare()`.
- `qed_remove()` reverses through `qed_hw_remove()`, PCI cleanup, power-state callback, and device free.

Slowpath and resource lifecycle:

- `qed_nic_setup()` marks non-Ethernet personalities as `using_ll2`, allocates resources, and performs resource setup.
- `qed_slowpath_start()` starts IOV and slowpath workqueues, loads firmware for PFs, acquires an aRFS PTT on single-hwfn PFs, allocates resources, configures interrupts, allocates zlib streams, initializes debug, starts hardware through `qed_hw_init()`, allocates `cdev->ll2` when any hwfn needs LL2, sends driver version to MFW, and resets vport stats.
- `qed_slowpath_stop()` stops workqueues, deallocates LL2 public state, releases PTT/stream/SR-IOV resources, stops hardware/tasklets/debug, frees IRQs/MSI-X, frees resources/IOV workqueue, and releases firmware.
- `qed_nic_stop()` calls `qed_hw_stop()`, disables SP tasklets, and exits PF debug state.

Interrupt handling:

- `qed_set_int_mode()` selects MSI-X, MSI, or INTa with fallback unless forced.
- `qed_enable_msix()` handles vector count negotiation and VF exact-vector requirements.
- `qed_slowpath_setup_int()` calculates requested slowpath/fastpath MSI-X vectors for PFs, handles kdump reduction, and partitions RDMA vectors away from L2 queues.
- `qed_slowpath_vf_setup_int()` configures VF MSI-X counts from VF queue information.
- `qed_slowpath_irq_req()`, `qed_slowpath_irq_sync()`, and `qed_slowpath_irq_free()` request/synchronize/free IRQs.
- `qed_single_int()` dispatches shared INTa/MSI slowpath and up to 64 fastpath handlers per hwfn.
- `qed_simd_handler_config()` and `qed_simd_handler_clean()` install/remove fastpath callback tokens.

Slowpath workqueue:

- `qed_slowpath_wq_start()` and `qed_slowpath_wq_stop()` manage per-hwfn workqueues for PFs.
- `qed_slowpath_delayed_work()` sets `slowpath_task_flags` with memory barriers and queues delayed work.
- `qed_slowpath_task()` processes MFW TLV requests and periodic doorbell recovery under a PTT, rescheduling if the PTT is unavailable.
- `qed_periodic_db_rec_start()` starts bounded periodic doorbell recovery.
- `qed_mfw_tlv_req()` queues immediate TLV processing.

Link and capability handling:

- `qed_set_link()` translates `struct qed_link_params` overrides into MCP link params, including legacy and extended speed advertisements, forced speeds, pause, loopback, EEE, and FEC, then calls `qed_mcp_set_link()`.
- `qed_set_ext_speed_params()` handles extended MFW speed and FEC encodings for 25/40/50/100G.
- `qed_get_link_data()` gathers link params/state/caps from MCP for PFs or VF bulletin paths for VFs.
- `qed_fill_link_capability()` maps media type, transceiver type, speed mask, and board config into phylink capability bits.
- `qed_fill_link()` fills `struct qed_link_output`, including link up/speed, supported/advertised/partner capabilities, pause, FEC, port, autoneg, and EEE.
- `qed_get_current_link()`, `qed_link_update()`, and `qed_bw_update()` expose link/bandwidth updates to protocol callbacks and VFs.

NVM/firmware helpers:

- `qed_nvm_flash()` loads a firmware file and interprets a QED NVM batch format.
- `qed_nvm_flash_image_validate()` validates signature, size, and max command id.
- `qed_nvm_flash_image_file_start()` and `qed_nvm_flash_image_file_data()` submit file upload chunks through MCP NVM writes.
- `qed_nvm_flash_image_access()` applies masked writes to NVM images or recalculates/writes image CRC via `qed_nvm_flash_image_access_crc()`.
- `qed_nvm_flash_cfg_write()`, `qed_nvm_flash_cfg_len()`, and `qed_nvm_flash_cfg_read()` write/read MFW NVM config attributes.
- `qed_nvm_get_image()` delegates image reads to MCP.

Common ops and callbacks:

- `qed_common_ops_pass` is the main exported vtable. It includes selftests, probe/remove, slowpath start/stop, interrupt info, SB init/release, link ops, debug/devlink, chain allocation, NVM flashing, coalescing, LED, recovery, PF updates, doorbell recovery, EEPROM reads, GRC config, MFW reports, SB debug, and ESL status.
- `qed_fill_dev_info()` fills `struct qed_dev_info` with PCI, tunnel, firmware, MFW, flash, WOL, ESL, SmartAN, RDMA, MAC, and MTU data.
- `qed_get_protocol_stats()` returns LAN/FCoE/iSCSI stats for MFW.
- `qed_mfw_fill_tlv_data()` fills generic or protocol TLV data for management firmware using protocol callbacks.
- `qed_hw_error_occurred()` and `qed_schedule_recovery_handler()` bridge hardware error/recovery notifications to protocol callbacks.

## Control flow

Probe begins with `qed_probe()`. It allocates a zeroed `qed_dev`, initializes common fields with `qed_init_struct()`, sets Linux driver type, protocol, VF flag, debug settings, and recovery state, then calls `qed_init_pci()`. PCI setup enables the device, checks BAR0 and PF BAR2, requests regions when the PCI enable count indicates first enable, enables bus mastering, saves state, rejects invalid revision id and non-PCIe devices, sets a 64-bit coherent DMA mask, maps BAR0 into `regview`, captures BAR2 doorbell physical/size, and maps doorbells write-combined for devices with BAR2. After PCI, `qed_hw_prepare()` initializes hardware-function structures and device metadata.

Slowpath start is the major bring-up sequence. `qed_slowpath_start()` first starts SR-IOV and per-hwfn slowpath workqueues. PFs request the versioned firmware blob and may acquire a PTT for aRFS. `qed_nic_setup()` marks non-Ethernet personalities as using LL2, allocates driver resources, and sets them up. Interrupt setup then selects PF or VF paths. PFs allocate zlib inflate streams so zipped firmware init data can be decompressed by `qed_unzip_data()`, and debug PF state is initialized. The function builds tunnel defaults, driver load params, and `qed_hw_init_params`, calls `qed_hw_init()`, sets tunnel feature masks, allocates `cdev->ll2` if `using_ll2`, sends driver version to MFW, and resets stats. The error path unwinds in reverse: LL2 dealloc, hardware stop/timer stop, IRQ free, stream free, MSI-X disable, resource free, firmware release, aRFS PTT release, IOV stop, and workqueue stop.

Slowpath stop reverses normal startup. It stops slowpath workqueues first to prevent new delayed work, frees the LL2 public object, releases aRFS PTT and zlib streams for PFs, disables SR-IOV for Ethernet PFs, calls `qed_nic_stop()`, frees slowpath IRQs, disables MSI/MSI-X, frees resources, stops IOV workqueues, and releases firmware.

Interrupt mode selection starts from requested mode. MSI-X allocates an `msix_table`, calls `qed_enable_msix()`, and falls through to MSI/INTa only if not forced. MSI is allowed only for single-hwfn devices. INTa is final fallback. Shared/single interrupt dispatch reads SISR per hwfn, schedules the slowpath tasklet for bit 0, and calls registered fastpath handlers for subsequent bits.

Link setting for PFs acquires a PTT on hwfn 0, edits the MCP link params in place according to override flags, uses speed maps to convert Linux ethtool link-mode masks into MFW bitfields, optionally fills extended speed/FEC fields, and calls `qed_mcp_set_link()`. For VFs it does not modify hardware and instead schedules a forced link query. Link reporting pulls MCP or VF bulletin state, maps media/transceiver/speed/board state into phylink masks, fills pause/FEC/EEE/autoneg/current speed fields, informs VFs, and calls the protocol `link_update` callback only from the leading hwfn.

NVM flashing parses a binary command stream. After validation, the loop reads a 32-bit command id and advances a `const u8 *data` cursor through command-specific parsers. Some commands set `check_resp`, after which `qed_nvm_flash()` fetches an MCP response and accepts only OK response codes. Config writes batch commits every `QED_NVM_CFG_MAX_ATTRS` attributes and use `QED_NVM_CFG_OPTION_INIT/COMMIT/FREE` flags.

## State and persistence behavior

Most state is runtime driver state stored in `struct qed_dev` and per-hwfn structures:

- PCI mappings: `cdev->regview`, `cdev->doorbells`, `db_phys_addr`, `db_size`, and `pci_params`.
- Interrupt state: `cdev->int_params`, MSI-X table, fastpath initialized flag, RDMA vector partitioning, tasklet requested/enabled flags, and SIMD fastpath handlers.
- Slowpath work state: per-hwfn `slowpath_wq`, `slowpath_task`, `slowpath_wq_active`, `slowpath_task_flags`, and periodic doorbell recovery counter.
- Firmware/debug state: `cdev->firmware`, per-hwfn zlib `stream`, debug PF state, aRFS PTT, and tunnel feature mask.
- Protocol state: `protocol`, `protocol_ops`, `ops_cookie`, `common_dev_info`, `ll2`, and `ll2_mac_address`.
- Recovery state: `recov_in_prog` and protocol-scheduled recovery/error callbacks.

Persistent device state can be changed through MCP operations in this file: NVM image writes, NVM config writes, wake-on-LAN/current configuration updates, MAC/MTU/driver-state overrides, LED mode, and link settings. Those operations are mediated by PTT acquisition and MCP helpers, not local disk writes.

The module-level speed maps are initialized once at module load. They use `__ro_after_init` map storage and discard original `__initconst` arrays after converting them into link-mode masks.

## Dependencies and integration points

The file integrates kernel PCI, DMA, IRQ, workqueue, firmware loading, zlib, ethtool link modes, phylink, devlink, CRC32, and crash dump APIs. It depends heavily on QED internal modules: hardware init/remove, resources, interrupts, MCP, SR-IOV, slowpath queue, LL2, FCoE, iSCSI, selftests, debug, devlink, and register definitions.

The LL2 integration point is important for this work item. `qed_nic_setup()` sets `p_hwfn->using_ll2 = true` for non-Ethernet personalities. Later `qed_slowpath_start()` calls `qed_ll2_alloc_if(cdev)` if the leading hwfn uses LL2; `qed_slowpath_stop()` calls `qed_ll2_dealloc_if(cdev)`. The actual LL2 queue start/stop and data-path operations are exported from `qed_ll2.c` through `qed_ll2_ops_pass`.

The common ops vtable is the core boundary to protocol drivers such as Ethernet, FCoE, iSCSI, RDMA, and management tooling. Protocol drivers call `probe`, `slowpath_start`, `get_fp_int`, `sb_init`, `set_link`, `nvm_flash`, and related functions through this table. The reverse callback boundary is `protocol_ops.common` and `ops_cookie`, used for link updates, bandwidth updates, recovery scheduling, hardware error scheduling, and TLV data collection.

## Risks and edge cases

- `qed_init_pci()` has direct `return -EINVAL`/`return -ENOMEM` paths after BAR mappings that bypass the shared `err2` unwind labels, which can leak earlier PCI resources or mappings if doorbell setup fails.
- Several NVM parser functions read unaligned little-endian fields via raw casts such as `*((u32 *)*data)` and `*((u16 *)*data)`. This is sensitive to alignment, endian assumptions, and bounds; validation checks total image size but individual command parsers do not visibly guard every cursor advance.
- `qed_set_link()` returns `-ENODATA` when `qed_mcp_get_link_params()` fails but does not release the acquired PTT before that return.
- `qed_alloc_stream_mem()` can return after partial allocation without freeing already allocated stream/workspace objects; the later global cleanup may handle some paths but direct failure accounting should be audited.
- `qed_free_stream_mem()` returns when it finds a hwfn without `stream`, potentially skipping later hwfns if partial allocation state is sparse.
- `qed_slowpath_start()` has many cross-module allocations and an intricate error unwind; changes should verify every acquisition has exactly one release on every failure path.
- Interrupt vector partitioning for RDMA depends on feature counts and hwfn count. Off-by-one or odd MSI-X counts can affect fastpath/RDMA vector exposure.
- Link capability mapping depends on MCP media/transceiver values and fallback speed masks. Unknown media defaults can under-report capabilities.
- `qed_fill_generic_tlv_data()` sets `rx_bytes_set = true` twice, likely intending `tx_bytes_set` for the TX byte counter.

## Test signals

Strong test coverage signals include PF and VF probe/remove cycles, slowpath start/stop under Ethernet and non-Ethernet personalities, firmware file missing/corrupt paths, MSI-X fallback to MSI/INTa, VF exact MSI-X rejection, CMT devices with multiple hwfns, kdump vector reduction, RDMA vector partitioning, LL2 allocation only for personalities that need it, link set/get for legacy and extended-speed capable firmware, media/transceiver matrix capability reporting, NVM flash validation and parser fault injection, MCP response error handling, workqueue cancellation during unload/recovery, periodic doorbell recovery scheduling, and protocol callback nullability.

Useful runtime instrumentation includes dynamic debug for `NETIF_MSG_DRV`, `NETIF_MSG_INTR`, and QED module masks; lockdep around workqueue/tasklet/IRQ stop; DMA API debugging for PCI mappings; firmware-class tests for missing and malformed files; KASAN/KMSAN for NVM parser bounds; and fault injection for `request_firmware()`, `pci_enable_msix_range()`, `qed_ptt_acquire()`, `qed_resc_alloc()`, `qed_hw_init()`, and MCP NVM writes.
