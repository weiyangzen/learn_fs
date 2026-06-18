# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_hw.c lines 9035-10774

## Purpose

This chunk is a hardware-support slice of the Chelsio `cxgb4` T4/T5/T6 adapter driver. It finishes serial-flash geometry detection, prepares adapter-wide software parameters, exposes emergency shutdown and BAR2 SGE queue-register mapping helpers, initializes cached firmware/SGE/TP/port state, provides diagnostic readers for CIM/TP/SGE state, and implements several firmware/flash-management operations used by ethtool, debugfs, SGE, and SR-IOV paths.

The code is not a standalone data path; it is the lower-level adapter-control layer used by higher-level probe/open, queue setup, debug collection, ethtool flashing, transceiver EEPROM reads, traffic scheduling, and VF ACL configuration.

## Important APIs, Types, and Functions

- `t4_get_flash_params()` tail: decodes JEDEC flash manufacturer/density values for ISSI, Macronix, and Winbond devices, falls back to a 4 MiB contract minimum, and persists `adapter->params.sf_size` and `adapter->params.sf_nsec`.
- `t4_prep_adapter()`: early adapter preparation. It reads PCI mode and PL revision, discovers flash size, maps `PCI_DEVICE_ID` high nibble to T4/T5/T6 chip parameters, initializes congestion-control defaults, installs fallback `nports`, `portvec`, and `vpd.cclk`, and sets PCIe completion timeout.
- `t4_shutdown_adapter()`: emergency path that disables interrupts/GPIO, drops per-port signal detect, and disables global SGE DMA.
- `t4_bar2_sge_qregs()`: converts an absolute SGE queue id into BAR2 page offset and BAR2 queue id, using cached SGE host-page and queues-per-page fields. It rejects kernel-mode T4 BAR2 queue registers.
- `t4_init_devlog_params()`: initializes `adapter->params.devlog` from a newer per-PF register when possible, otherwise via `FW_DEVLOG_CMD`.
- `t4_init_sge_params()`: caches PF-specific SGE host page size, egress queues/page, and ingress queues/page in `struct sge_params`.
- `t4_init_tp_params()` and `t4_filter_field_shift()`: cache TP timer resolution, delayed-ACK resolution, filter mode/mask, ingress configuration, T6 encapsulation handling, compressed-filter field shifts, and hash-filter mask.
- `t4_init_rss_mode()`, `t4_init_portinfo()`, `t4_port_init()`, `t4_init_port_mirror()`: firmware-backed VI/port initialization. They negotiate 16-bit versus 32-bit port capabilities, allocate VIs, store `struct port_info` fields, initialize link config, and set netdev MAC addresses.
- CIM/TP diagnostics: `t4_read_cimq_cfg()`, `t4_read_cim_ibq()`, `t4_read_cim_obq()`, `t4_cim_read()`, `t4_cim_write()`, `t4_cim_read_la()`, and `t4_tp_read_la()` read queue configuration, debug queue contents, CIM internal address space, and CIM/TP logic-analyzer captures.
- IDMA diagnostics: `t4_idma_monitor_init()` and `t4_idma_monitor()` synthesize longer SGE ingress-DMA stall timers from hardware same-state counters and issue repeated warnings with decoded IDMA state.
- Flash/config writes: `t4_load_cfg()`, `modify_device_id()`, `t4_load_boot()`, `t4_flash_bootcfg_addr()`, and `t4_load_bootcfg()` erase and program firmware config, option ROM, and option-ROM configuration flash regions.
- VF and scheduler helpers: `t4_set_vf_mac_acl()`, `t4_set_vlan_acl()`, `t4_read_pace_tbl()`, `t4_get_tx_sched()`, and `t4_sched_params()`.
- SGE/I2C helpers: `t4_sge_ctxt_rd()`, `t4_sge_ctxt_rd_bd()`, and `t4_i2c_rd()`.

Key surrounding types/constants come from `cxgb4.h` and `t4_hw.h`: `struct adapter_params`, `struct sge_params`, `struct tp_params`, `struct devlog_params`, `struct sge_idma_monitor_state`, `struct port_info`, `enum t4_bar2_qtype`, boot ROM header structures, `FLASH_*` section constants, `BOOT_*` signatures/sizes, and `I2C_PAGE_SIZE`.

## Control Flow

Early hardware bring-up flows through `t4_prep_adapter()`. The function first requires flash identification to succeed. It then reads PCI device id, chooses T4/T5/T6 architecture constants, and records chip-specific capabilities such as MPS TCAM size, replacement table size, channel count, PM counter count, VF count, SGE free-list doorbell encoding, and congestion-channel bit width. Unsupported devices fail with `-EINVAL`. The routine also sets fallback values that keep debug paths usable before firmware discovery completes.

BAR2 queue mapping depends on previous SGE parameter initialization. `t4_bar2_sge_qregs()` computes a BAR2 page from `qid >> qpp_shift`, computes the queue's offset within that page, and returns either an inferred queue-id mode (`*pbar2_qid = 0`, offset includes the queue slot) or an explicit BAR2 queue-id mode (offset is the page base and `*pbar2_qid` is nonzero).

TP initialization first reads direct TP timing registers, initializes default TX modulation queue mapping, and tries the firmware parameter API for filter mode/mask. If firmware is too old, it falls back to indirect TP register reads and sets `filter_mask` equal to the filter mode to preserve older validation behavior. It then reads ingress config, T6 outer-header encapsulation state, computes all compressed-filter field shifts, applies the VNID/VLAN special case, and reads the 64-bit hash-filter mask from two LE registers.

Port initialization is firmware-driven. `t4_init_portinfo()` enables 32-bit port capabilities with a PF/VF parameter if supported, selects the corresponding `FW_PORT_CMD` action, extracts port type, MDIO address, and capabilities, allocates a VI, and stores VI/RSS/channel/link fields in `struct port_info`. `t4_port_init()` iterates logical driver ports over `adapter->params.portvec`, calls `t4_init_portinfo()`, and installs the firmware-assigned MAC address into the netdev. `t4_init_port_mirror()` is a narrow VI allocation path for mirror VIs.

Diagnostic readers follow hardware busy/probe protocols. CIM queue readers select an IBQ/OBQ, clamp requested word count to hardware queue size, drive debug address/config registers, wait for busy bits to clear, read data registers, and disable debug read mode afterward. CIM address-space access fails immediately if `HOSTBUSY` is already set, then performs word-by-word read/write transactions. Logic analyzer readers try to preserve running state: CIM LA freezes if enabled, captures from the hardware write pointer, handles T6's 312-bit entry addressing gap, and restarts on exit; TP LA similarly freezes/restores and marks the last entry invalid if the hardware says it is incomplete.

Flash update paths are erase-then-program. `t4_load_cfg()` locates the firmware config region, validates max size, erases the entire config span, treats `size == 0` as clear-only, then writes page-sized chunks with `t4_write_flash(..., true)`. `t4_load_boot()` validates that the option ROM does not reach firmware sectors, checks ROM/PCIR signatures and Chelsio vendor id, erases the requested boot span, normalizes the PCIR device id to current PF0 hardware if needed, writes all pages except the first, then writes the first page last so the boot header only appears after the body has programmed. `t4_load_bootcfg()` validates flash capacity and signature, erases the bootcfg sector, writes page chunks, and pads to 4-byte alignment with zero bytes.

## State and Persistence Behavior

The main persistent software state is under `adapter->params` and `struct port_info`. This chunk fills flash geometry (`sf_size`, `sf_nsec`), chip architecture (`chip`, `arch.*`), fallback port/VPD values, devlog location (`devlog.memtype/start/size`), SGE BAR2 geometry (`sge.hps`, `eq_qpp`, `iq_qpp`), TP filter/timing/hash state (`tp.*`), firmware capability mode (`fw_caps_support`), and per-port VI/link/RSS/channel identity.

Hardware-persistent state is changed in several places:

- `t4_shutdown_adapter()` disables interrupts, GPIO, link signal detect, and SGE global enable until later reinitialization.
- `t4_load_cfg()`, `t4_load_boot()`, and `t4_load_bootcfg()` erase/write serial flash regions and are therefore persistent across reset/power cycles.
- `modify_device_id()` mutates the in-memory boot image before flash programming, including legacy-ROM checksum recomputation.
- `t4_set_vf_mac_acl()` and `t4_set_vlan_acl()` issue firmware ACL commands affecting VF policy.
- `t4_sched_params()` issues firmware scheduler parameter writes.
- CIM/TP LA readers temporarily freeze debug capture state but try to restore the previous running configuration.

`t4_idma_monitor()` maintains transient monitor state in `struct sge_idma_monitor_state`: one-second core-clock threshold, synthesized stalled timers in `HZ` units, last observed IDMA state, queue id, and warning repeat countdown.

## Dependencies and Integration Points

This chunk depends on direct register helpers (`t4_read_reg`, `t4_write_reg`, `t4_read_reg64`, `t4_set_reg_field`, `t4_wait_op_done`), firmware mailbox helpers (`t4_wr_mbox`, `t4_wr_mbox_meat`, `t4_query_params`, `t4_set_params`, `t4_alloc_vi`), flash helpers (`t4_flash_cfg_addr`, `t4_flash_erase_sectors`, `t4_write_flash`), indirect TP helpers (`t4_tp_pio_read`, `t4_tp_tm_pio_read`), conversion helpers (`core_ticks_per_usec`, `dack_ticks_to_usec`, capability conversion and link-config initialization), and PCI/kernel primitives (`pci_read_config_word`, `pcie_capability_clear_and_set_word`, `eth_hw_addr_set`, endian conversion, `dev_*` logging).

External call sites show the intended integration:

- `sge.c` uses `t4_bar2_sge_qregs()` for queue doorbell/register placement and calls the IDMA monitor from RX queue checking.
- `cxgb4_main.c` calls TP and port initialization during adapter bring-up and uses VLAN ACL setup for VF configuration.
- `cxgb4_ethtool.c` routes firmware flashing subtypes to `t4_load_boot()`/`t4_load_bootcfg()` and reads module EEPROM/diagnostics through `t4_i2c_rd()`.
- `cxgb4_debugfs.c` and `cudbg_lib.c` consume CIM queue dumps, devlog parameters, and SGE context reads.
- `sched.c`/traffic-control code uses scheduler parameter programming through firmware.

## Risks and Edge Cases

- Flash geometry fallback assumes any unknown flash is at least 4 MiB with 64 KiB sectors. This matches the documented hardware/software contract but could mis-size unsupported hardware and cause `FLASH_MIN_SIZE` warnings.
- `t4_bar2_sge_qregs()` relies on `t4_init_sge_params()` having populated `hps`, `eq_qpp`, and `iq_qpp`; stale or zero values would produce bad BAR2 offsets.
- `t4_set_vf_mac_acl()` does not validate `start` beyond cases 0-3 and copies full fixed fields from `addr`; callers must ensure `naddr`, `start`, and buffer length are coherent.
- `t4_set_vlan_acl()` accepts an `mbox` argument but calls `t4_wr_mbox()` with `adap->mbox`, which may be intentional driver convention or an argument-use bug.
- `t4_load_bootcfg()` documents `size == 0` as clear-only, but it dereferences `cfg_data` and checks `header->signature` before the `size == 0` branch. A caller passing `NULL, 0` like `t4_load_cfg()` supports would fault; callers must pass a valid header buffer or this path needs reordering.
- `t4_load_boot()` validates top-level ROM and first PCIR header before erasing, but `modify_device_id()` walks chained images using image-provided lengths/offsets without an explicit total-size bound in this function.
- `t4_load_boot()` writes full `SF_PAGE_SIZE` chunks after subtracting one page; the prior size validations and ethtool classification need to ensure option ROM image size is page-aligned enough for that loop.
- Logic-analyzer readers alter debug configuration while collecting dumps. They restore state, but failures during freeze/read/restart can leave hardware capture disabled or partially repositioned.
- `t4_i2c_rd()` intentionally rejects reads larger than one 256-byte page and reads spanning the A0/A2-style page boundary; higher layers split multi-page EEPROM reads.

## Test Signals

- Probe/bring-up on T4, T5, and T6 hardware should report correct chip architecture parameters, PCIe completion timeout setup, flash size/sector count, TP filter mode/mask, and initialized netdev MAC addresses.
- BAR2 queue tests should cover user versus kernel queues, T4 kernel rejection, ingress/egress qpp differences, inferred queue-id offsets, and explicit queue-id offsets when `bar2_qid_offset >= page_size`.
- Firmware compatibility tests should cover both 32-bit and 16-bit port capability paths and the old-firmware TP filter fallback.
- Debug collection should validate CIM IBQ/OBQ reads, CIM and TP LA dumps, SGE context reads through firmware and backdoor, and IDMA stall/resume warnings under simulated or hardware-induced stuck states.
- Flashing tests should exercise config load and clear, boot ROM validation failures, boot ROM device-id rewrite/checksum update, first-page-last programming, bootcfg signature validation, 4-byte padding, and error reporting on erase/write failures.
- SR-IOV tests should verify VF MAC ACL and VLAN ACL mailbox commands, including VLAN zero disable behavior and packet-drop policy when a VLAN is enabled.
- I2C/module EEPROM tests should verify one-page reads, boundary rejection, split reads in ethtool callers, and firmware mailbox error propagation.
