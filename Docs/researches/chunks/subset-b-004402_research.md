# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4_hw.c lines 1-9034

## Scope

This chunk covers the first 9,034 lines of the Chelsio `cxgb4` T4/T5/T6 hardware support implementation. It includes low-level register and memory-window access, firmware mailbox serialization, flash/VPD/firmware image management, link capability translation and L1 configuration, global hardware error interrupt handlers, RSS and TP table/stat helpers, port/MPS statistics, MAC filter and VI resource firmware commands, queue teardown commands, link event processing, PCI/link state helpers, device-ready polling, and the beginning of serial-flash parameter discovery.

The range stops inside `t4_get_flash_params()`, just before `t4_prep_adapter()` starts. Later adapter preparation, SGE/TP parameter initialization, port initialization, CIM/TP logic analyzer readers, boot/config flashing, scheduler commands, and other debug/config helpers are outside this chunk.

## Purpose

`t4_hw.c` is the shared hardware/firmware control layer for Chelsio T4-family Ethernet adapters. In this chunk it provides the primitives used by probe, ethtool, link management, resource setup, filtering, diagnostics, and reset paths to safely interact with the adapter:

- Serialize and execute firmware mailbox commands with timeout handling, reply logging, firmware assertion decoding, and firmware-error reporting.
- Access chip registers, indirect register files, PCI configuration space, adapter memory windows, serial EEPROM/VPD, and serial flash.
- Validate, load, upgrade, halt, restart, and version firmware and PHY firmware images.
- Translate firmware port capability formats into driver link state, issue L1 link configuration commands, and process firmware link-change replies.
- Handle top-level non-data hardware interrupts from PCIe, CIM, SGE, TP, MPS, memory, PM, ULP, LE, MAC, SMB, NC-SI, and PL modules, escalating fatal conditions through `t4_fatal_err()`.
- Configure and inspect RSS, TP, MTU/congestion-control tables, trace filters, MPS buffer group mappings, MAC filters, VI state, and queue resources.
- Collect adapter, port, loopback, TP, PM, FCoE, RDMA, and USM counters for ethtool/debug consumers.

Although this file lives under a `ceph-client` mirror, the code is Linux kernel network-driver code for Chelsio hardware, not Ceph filesystem logic.

## Important APIs, Types, And Data Structures

- `struct adapter` is the central hardware object. This chunk reads and mutates fields such as `params`, `flags`, `pf`, `mbox`, `pdev`, `pdev_dev`, `mbox_log`, `mlist`, `mbox_lock`, `win0_lock`, `use_bd`, and cached values like `params.sf_size`, `params.sf_nsec`, `params.fw_vers`, `params.tp_vers`, `params.pfres`, and `params.mps_bg_map`.
- `struct link_config` and `struct port_info` carry per-port state: physical capabilities (`pcaps`), advertised capabilities (`acaps`), link partner capabilities, current speed, flow-control, FEC, autonegotiation state, module type, link-down reason, VI ID, port IDs, and OS notification hooks.
- Firmware command structs from `t4fw_api.h` are the ABI payloads for most control operations: `fw_ldst_cmd`, `fw_port_cmd`, `fw_params_cmd`, `fw_pfvf_cmd`, `fw_vi_cmd`, `fw_vi_rxmode_cmd`, `fw_vi_mac_cmd`, `fw_vi_enable_cmd`, `fw_iq_cmd`, and egress queue commands.
- Register and field macros from `t4_regs.h`, `t4_values.h`, and `t4_chip_type.h` define chip-specific register addresses, bit fields, and chip-generation selectors used throughout the chunk.
- `struct intr_info` is the table-driven interrupt action descriptor: a mask, optional log message, fatal flag, and optional subhandler. The various module handlers instantiate static tables for parity, ECC, FIFO, framing, illegal-access, timeout, and firmware-error causes.
- `struct fw_hdr` is used for firmware compatibility checks, flash validation, image checksums, image versioning, and deciding whether a restart requires a full reset.
- `struct vpd_params`, `struct pf_resources`, `struct port_stats`, `struct lb_port_stats`, `struct tp_*_stats`, and `struct trace_params` are filled by VPD/resource/stat/trace accessors for upper layers such as probe and ethtool.
- `struct mbox_cmd_log` records command/reply flits, sequence numbers, timestamps, and access/execute timing for firmware mailbox debugging.

Key public entry points in this chunk include:

- Register/memory access: `t4_set_reg_field()`, `t4_read_indirect()`, `t4_write_indirect()`, `t4_hw_pci_read_cfg4()`, `t4_read_pcie_cfg4()`, `t4_get_util_window()`, `t4_setup_memwin()`, `t4_memory_rw_init()`, `t4_memory_update_win()`, `t4_memory_rw_residual()`, `t4_memory_rw()`, `t4_get_regs_len()`, and `t4_get_regs()`.
- Firmware mailbox and lifecycle: `t4_wr_mbox_meat_timeout()`, `t4_wr_mbox_meat()`, `t4_fw_hello()`, `t4_fw_bye()`, `t4_early_init()`, `t4_fw_reset()`, `t4_fw_upgrade()`, `t4_fw_initialize()`, `t4_query_params_rw()`, `t4_query_params()`, `t4_query_params_ns()`, `t4_set_params_timeout()`, and `t4_set_params()`.
- Flash/VPD/firmware: `t4_eeprom_ptov()`, `t4_seeprom_wp()`, `t4_get_raw_vpd_params()`, `t4_get_vpd_params()`, `t4_read_flash()`, `t4_get_fw_version()`, `t4_get_bs_version()`, `t4_get_tp_version()`, `t4_get_exprom_version()`, `t4_get_vpd_version()`, `t4_get_scfg_version()`, `t4_get_version_info()`, `t4_dump_version_info()`, `t4_check_fw_version()`, `t4_prep_fw()`, `t4_load_fw()`, `t4_phy_fw_ver()`, `t4_load_phy_fw()`, and `t4_fwcache()`.
- Link and port handling: `t4_link_acaps()`, `t4_link_l1cfg_core()`, `t4_restart_aneg()`, `t4_handle_get_port_info()`, `t4_update_port_info()`, `t4_get_link_params()`, `t4_handle_fw_rpl()`, and `init_link_config()`.
- Interrupt handling: `t4_slow_intr_handler()`, `t4_intr_enable()`, `t4_intr_disable()`, and module-specific static handlers such as `pcie_intr_handler()`, `sge_intr_handler()`, `cim_intr_handler()`, `mps_intr_handler()`, `mem_intr_handler()`, and `xgmac_intr_handler()`.
- RSS/TP/stats/diagnostics: `t4_config_rss_range()`, `t4_config_glbl_rss()`, `t4_config_vi_rss()`, `t4_read_rss()`, `t4_read_rss_key()`, `t4_write_rss_key()`, `t4_read_rss_pf_config()`, `t4_read_rss_vf_config()`, `t4_tp_pio_read()`, `t4_tp_tm_pio_read()`, `t4_tp_mib_read()`, `t4_tp_get_tcp_stats()`, `t4_tp_get_err_stats()`, `t4_tp_get_cpl_stats()`, `t4_tp_get_rdma_stats()`, `t4_get_fcoe_stats()`, `t4_get_usm_stats()`, `t4_read_mtu_tbl()`, `t4_read_cong_tbl()`, `t4_load_mtus()`, `t4_get_chan_txrate()`, `t4_set_trace_filter()`, `t4_get_trace_filter()`, `t4_pmtx_get_stats()`, `t4_pmrx_get_stats()`, `t4_get_mps_bg_map()`, `t4_get_tp_ch_map()`, `t4_get_port_stats()`, and `t4_get_lb_stats()`.
- Resource and filter commands: `t4_get_pfres()`, `t4_cfg_pfvf()`, `t4_alloc_vi()`, `t4_free_vi()`, `t4_set_rxmode()`, `t4_alloc_mac_filt()`, `t4_free_mac_filt()`, `t4_change_mac()`, `t4_set_addr_hash()`, raw/encap MAC filter helpers, `t4_enable_vi_params()`, `t4_enable_vi()`, `t4_enable_pi_params()`, `t4_identify_port()`, `t4_iq_stop()`, `t4_iq_free()`, `t4_eth_eq_free()`, `t4_ctrl_eq_free()`, and `t4_ofld_eq_free()`.

## Control Flow

The mailbox path is the central control-flow primitive. `t4_wr_mbox_meat_timeout()` first validates command size and PCI channel state, queues the caller on `adapter->mlist` under `mbox_lock`, waits until the caller reaches the head, then verifies mailbox ownership. It writes command flits into PF mailbox data registers, transfers ownership to firmware, polls with either sleep or busy delays, decodes replies, handles `FW_DEBUG_CMD` assertions through `fw_asrt()`, copies optional replies, clears the mailbox control register, records both command and reply in `mbox_log`, removes the caller from the mailbox queue, and returns the negative firmware status on failure. Timeouts, firmware error bits, and mailbox ownership failures are logged; hard timeouts also call `t4_report_fw_error()` and `t4_fatal_err()`.

Adapter memory access uses PCIe memory windows. `t4_memory_rw()` validates 32-bit alignment for the adapter address and host buffer, normalizes the length into word transfers plus a residual byte tail, calls `t4_memory_rw_init()` to map a memory type (`MEM_EDC0`, `MEM_EDC1`, `MEM_MC`, `MEM_MC1`, or `MEM_HMA`) to an offset/base/aperture, positions the selected memory window with `t4_memory_update_win()`, then streams little-endian-corrected 32-bit register reads or writes. When the transfer crosses a window aperture it advances the window. Residual bytes are handled by `t4_memory_rw_residual()`. Callers such as PHY firmware download serialize shared window use with `win0_lock`.

Flash and firmware control starts with low-level `sf1_write()`, `sf1_read()`, and `flash_wait_op()` helpers. `t4_read_flash()` validates bounds/alignment, issues fast-read serial-flash commands, and optionally preserves byte-oriented image order. `t4_write_flash()` writes at most one 256-byte page after write-enable, waits for flash completion, unlocks the serial flash, and verifies the written page by reading it back. `t4_load_fw()` validates firmware size, header length, chip type, and checksum, erases the needed sectors, writes the first page with an intentionally invalid version, writes the remaining pages, and only then writes the real version field so interrupted updates do not look valid. `t4_fw_upgrade()` clears `CXGB4_FW_OK`, halts firmware, writes the image, clears any old firmware configuration file via `t4_load_cfg()` outside this chunk, restarts or resets firmware depending on image capability flags, refreshes devlog parameters, then restores `CXGB4_FW_OK`.

Firmware selection is layered. `t4_prep_fw()` reads the card firmware header from flash, compares it with the driver-supported header via `fw_compatible()`, optionally compares filesystem firmware, decides whether to install filesystem firmware with `should_install_fs_fw()`, and either upgrades in `DEV_STATE_UNINIT` or rejects the card if no usable firmware exists. `t4_check_fw_version()` separately enforces minimum chip-specific firmware versions.

PHY firmware download uses firmware-mediated staging. `t4_load_phy_fw()` optionally compares the image version with the currently loaded PHY firmware, asks firmware for a target memory type/address by querying `FW_PARAMS_PARAM_DEV_PHYFW_DOWNLOAD` with the image size, copies the image through the PCIe memory window, then sends a set-params command with a long timeout to make firmware copy the image to the PHYs and reset them. If a version parser was supplied, it re-queries the PHY firmware version and reports mismatch as `-ENXIO`.

Link configuration converts between several representations. The helper pair `fwcaps16_to_caps32()` and `fwcaps32_to_caps16()` handles legacy and newer firmware capability formats. `t4_link_acaps()` combines base advertised capabilities with requested pause, FEC, MDI, speed, and autonegotiation controls, validates the result against physical capabilities, and updates `link_config` fields for forced or autonegotiated modes. `t4_link_l1cfg_core()` packages that into `FW_PORT_ACTION_L1_CFG` or `FW_PORT_ACTION_L1_CFG32`. `t4_restart_aneg()` sends a minimal L1 config with autonegotiation set.

Link status is updated from firmware port replies. `t4_handle_get_port_info()` accepts either 16-bit `GET_PORT_INFO` or 32-bit `GET_PORT_INFO32`, extracts link state, link-down reason, port type, module type, physical/advertised/link-partner capabilities, and link attributes, then updates `link_config`. Module changes update `pcaps`, default advertised capabilities, cached port/module type, set `new_module`, and notify `t4_os_portmod_changed()`. Link changes update speed, flow-control, FEC, partner caps, autonegotiation fields, issue ratelimited link-down logs, and notify `t4_os_link_changed()`. If a new module requires sticky L1 reconfiguration, the old link config is restored on command failure.

The slow interrupt path reads `PL_INT_CAUSE_A`, masks it with `PL_INT_ENABLE_A`, dispatches the enabled global module bits, then clears processed global causes. Each module handler uses `t4_handle_intr_status()` tables or custom register decoding to log warnings/alerts, clear module cause registers, and call `t4_fatal_err()` for fatal parity/ECC/framing/illegal-access conditions. SGE handling additionally logs doorbell FIFO callbacks, parity cause registers, captured queue IDs, and uncaptured error flags. CIM handling gives firmware crash indication priority by reading `PCIE_FW_A` and suppressing non-crash timer0 interrupts.

RSS and TP control mix firmware commands and backdoor register access. RSS indirection writes are split into firmware commands with up to 32 entries each. `t4_tp_indirect_rw()` prefers firmware LDST access for TP PIO/TM/MIB spaces when firmware is healthy and backdoor access is not required; otherwise it falls back to indirect address/data register pairs. These helpers drive RSS key reads/writes, PF/VF RSS config inspection, TP MIB statistics, MTU and congestion-control table programming, and trace-filter configuration.

Virtual-interface and filter management is command-oriented. VI allocation sends `FW_VI_CMD` and extracts assigned MAC addresses, VI ID, RSS size, VF-valid, and VIN. RX mode, VI enable, port identification, and queue stop/free all become small firmware commands. Exact MAC filters are allocated in batches, with `-FW_ENOMEM` treated as a partial success so successfully allocated entries and optional hash fallbacks are still reported. `t4_change_mac()` may request an SMT result as well as an MPS TCAM entry and has chip-specific fallback SMT-index derivation when firmware does not expose the extended VIID SMT field. Raw and encapsulated MAC filter helpers program MPS TCAM-style entries for tunnel/inner or outer matching.

The chunk ends while `t4_get_flash_params()` is decoding JEDEC flash IDs. It reads the serial flash ID, checks a small supported part table, decodes manufacturer-specific density fields for Micron/Numonix, ISSI, Macronix, and Winbond, and falls back to a 4MB assumption for unknown parts. The final storage of `sf_size`/`sf_nsec` and minimum-size warning are just at the boundary.

## State And Persistence Behavior

- Firmware mailbox state is transient in registers but persistent enough to require host-side serialization. `adapter->mlist` orders concurrent command senders, `mbox_lock` protects that queue, and `mbox_log` persists recent command/reply history for debugging.
- `adapter->flags` reflects firmware health and access policy. `CXGB4_FW_OK` is cleared on firmware-reported errors and during firmware flashing; several paths avoid firmware LDST access unless this flag is set.
- Firmware and device versions persist in `adapter->params`: firmware, bootstrap, TP microcode, expansion ROM, VPD revision, serial configuration revision, VPD identity strings, and core clock.
- Serial flash and EEPROM are nonvolatile. This chunk can modify EEPROM write-protect state, firmware flash contents, and by extension invalidate or erase firmware configuration content during upgrades through the out-of-range `t4_load_cfg()` call.
- PHY firmware may be persistent or RAM-backed depending on the adapter. `t4_load_phy_fw()` explicitly notes that RAM-backed PHY firmware must be loaded after adapter reset because reset can discard it.
- `struct link_config` persists the last known link state and user/sticky requested controls across firmware link replies. It also caches `def_acaps` so later FEC auto behavior can use module-derived defaults.
- Hardware register state persists until reset or later reconfiguration: memory-window base/offset registers, SGE host page size and buffer-size registers, SGE interrupt enable bits, TP MTU/congestion/RSS tables, trace filter registers, MPS stats mode interpretation, and VI/filter resources allocated in firmware.
- `adapter->params.mps_bg_map[]` caches firmware-provided or computed MPS buffer-group maps to avoid repeated firmware queries.
- Firmware resources such as VIs, MAC filters, ingress queues, and egress queues live in firmware until explicit free commands or adapter reset. This chunk mostly allocates/frees/configures those resources; software ownership tracking is in surrounding driver code.
- Statistics counters are hardware-maintained and monotonic until reset or hardware clear. `t4_get_port_stats_offset()` computes deltas against a caller-provided snapshot but does not persist that snapshot itself.

## Dependencies And Integration Points

- Linux kernel PCI, VPD, delay, logging, endian, vmalloc, and MMIO APIs: `pci_read_vpd()`, `pci_write_vpd()`, `pci_vpd_find_*()`, `pci_vpd_check_csum()`, `pci_is_pcie()`, `pcie_capability_read_word()`, `readl()`, `msleep()`, `mdelay()`, `udelay()`, `dev_err()`, `dev_warn()`, `dev_alert()`, and `dev_info()`.
- Driver-local register accessors and helpers: `t4_read_reg()`, `t4_write_reg()`, `t4_read_reg64()`, `t4_write_reg64()`, `t4_fatal_err()`, `t4_db_full()`, `t4_db_dropped()`, `t4_os_link_changed()`, `t4_os_portmod_changed()`, `t4_is_inserted_mod_type()`, `hash_mac_addr()`, `for_each_port()`, and `adap2pinfo()`.
- Firmware ABI definitions from `t4fw_api.h` drive command layout, capability fields, return codes, mailbox ownership, LDST address spaces, firmware device parameters, port actions, VI commands, queue commands, and firmware image headers.
- Chip-generation differences are pervasive. T4, T5, and T6 differ in register maps, PCIe config backdoor enable bits, SGE packing/padding semantics, RSS table size and key addressing, interrupt masks, MPS port/register offsets, MAC interrupt register names, memory-controller layout, and flash/firmware assumptions.
- Ettool and diagnostics integrate through register dumps, VPD/version reporting, flash operations, trace filters, stats readers, RSS readers/writers, link parameter readers, and port identify LED control.
- Probe/open/resource-management code outside this chunk calls the firmware hello/reset/init path, configures PF/VF limits, allocates VIs, updates port information, and frees queues/filters during teardown.
- The data path depends on state programmed here: SGE host page/free-list alignment, RSS table/key configuration, VI RX mode, MAC filters, link status, queue resources, and interrupt enablement.

## Risks And Edge Cases

- Mailbox commands can fail in several distinct phases: queue wait, mailbox ownership, firmware execution, firmware assertion, PCI channel offline, firmware error bit, or timeout. Callers must not treat all negative returns as equivalent because some indicate firmware/hardware fatality.
- `t4_wr_mbox_meat_timeout()` uses a command-size multiple-of-16 requirement and writes 64-bit flits. Incorrect command sizing or stale command structs can produce firmware ABI failures that are hard to diagnose.
- The mailbox access wait has a coarse global timeout not based on queue position. Heavy contention could return `-EBUSY` even when firmware is otherwise healthy.
- The timeout path calls `t4_fatal_err()`. A slow firmware operation with an insufficient timeout can escalate to a fatal adapter state.
- Memory-window reads/writes require 32-bit address and host-buffer alignment. The function supports residual byte length, but not unaligned starting addresses or buffers.
- `t4_memory_rw_residual()` is subtle: the read path copies bytes from offset to byte 3 into the provided residual buffer; the write path starts from `*buf` and zeroes bytes from the offset onward before writing. Any caller misunderstanding the residual-offset convention can corrupt a trailing word.
- Flash writes are destructive and persistent. `t4_load_fw()` protects against interrupted updates by writing an invalid version first, but a failed erase/write can still leave the adapter without usable firmware until reflashed.
- `t4_fw_upgrade()` clears existing firmware configuration via `t4_load_cfg(adap, NULL, 0)` after firmware load. This prevents incompatible config use but also removes a persistent configuration file and requires the user/admin to provide a compatible one later if needed.
- Firmware restart/halt paths can force the microprocessor into reset without firmware cooperation. The comments explicitly warn that failed forced upgrades may leave the adapter in a badly broken state.
- Version compatibility depends on firmware interface fields, not only numeric version. Filesystem firmware is installed only when compatible and when the adapter is uninitialized; otherwise an unusable card firmware path fails.
- Unknown flash parts are accepted as 4MB with 64KB sectors per hardware contract. If a future unsupported part violates that contract, flash addressing and erase counts would be wrong.
- Link capability handling must keep `t4_link_acaps()`, `t4_handle_get_port_info()`, and `init_link_config()` in parallel. Divergence can make forced speed/autoneg/FEC/pause settings inconsistent across initial state, user configuration, and firmware events.
- `t4_link_acaps()` returns `-EINVAL` cast into `fw_port_cap32_t` on physical-capability overflow. The immediate caller stores it in an unsigned capability variable before sending a command. The firmware rejection path catches invalid combinations, but the mixed return type is fragile.
- `t4_handle_fw_rpl()` assumes a matching `port_info` is found for a firmware port ID. If no match exists, it can pass a stale or null `pi` to `t4_handle_get_port_info()` depending on loop behavior.
- SGE IDMA decode first selects T6-specific decode strings, then immediately overrides non-T4 chips to the T5 table. That makes the T6 table effectively unused in this chunk and may mislabel T6 IDMA states.
- Interrupt handling is intentionally fatal for many parity/ECC conditions. Tests or error injection that trigger these bits can take down the adapter instead of merely logging.
- Several interrupt handlers clear only masks they process. Unexpected bits may remain set and retrigger if not covered by the tables.
- RSS key writes for T6 extended key mode depend on `KEYEXTEND` and `KEYMODE == 3`. Wrong mode detection can write the wrong key-table index.
- MAC filter allocation treats firmware ENOMEM as partial success. Callers must inspect returned indexes and hash fallback bits rather than assuming all requested exact filters exist.
- `t4_set_rxmode()` mirrors commands to `viid_mirror` only after the main VI command succeeds. A mirror command failure can leave mirrored VIs with divergent RX modes.
- Port statistics adjust pause-frame counts based on `MPS_STAT_CTL_A` flags on T5+. Incorrect flag interpretation can underflow unsigned counters when hardware already excludes pause frames.

## Test And Validation Signals

- Build coverage with `CONFIG_CHELSIO_T4` and representative T4, T5, and T6 compile paths. Important compile signals include firmware command struct layout, register macro availability, `fallthrough` handling, and chip-generation conditionals.
- Probe smoke tests should show successful device-ready polling, firmware hello, VPD read, flash parameter discovery, version reads, PF resource query, and link configuration initialization.
- Mailbox tests should cover successful command/reply, non-sleeping commands, negative timeout behavior, firmware busy/timeouts, firmware assertion replies, PCI channel offline, and mailbox log entries with access/execute timing.
- Firmware management tests should exercise card firmware compatible path, filesystem firmware upgrade path in `DEV_STATE_UNINIT`, incompatible firmware rejection, corrupted checksum rejection, interrupted/failed flash write behavior, and post-upgrade restart/reset behavior.
- Serial flash tests should cover JEDEC ID decoding for known manufacturers, fallback unknown ID behavior, read bounds/alignment checks, page write verification, sector erase failures, and `sf_size`/`sf_nsec` values.
- Memory-window tests should read and write EDC/MC/HMA memory across aperture boundaries, verify endian-correct byte order, test residual lengths, and confirm `win0_lock` protects shared-window callers.
- Link tests should exercise both 16-bit and 32-bit firmware capability paths, forced speed, autonegotiation restart, pause and FEC combinations, module insertion/removal events, link-down reason logging, and sticky L1 reconfiguration on new modules.
- Interrupt tests should inject or simulate per-module parity/ECC/framing/illegal-access causes and verify table-driven logging, cause clearing, fatal escalation, and no handling when top-level cause bits are disabled.
- RSS/TP tests should program global/VI RSS modes, indirection ranges larger than 32 entries, RSS key table entries including T6 extended key indexes, PF/VF RSS config reads, MTU/congestion table loads, and LDST fallback to indirect backdoor access.
- Statistics tests should compare port, loopback, TP, PMTX/PMRX, FCoE, RDMA, USM, channel rate, MPS buffer group, and TP channel map outputs against hardware counters and firmware-provided maps.
- VI/filter/resource tests should allocate/free VIs, set RX modes including mirror VIs, allocate exact MAC filters with partial ENOMEM, hash fallback, raw and encapsulated MAC filters, address changes with SMT index output, VI enable/disable link notification, LED identify, and queue stop/free teardown.

## Chunk Notes For Merge Lane

This chunk is the hardware/firmware control foundation for `t4_hw.c`. The next chunk should connect the partial flash-parameter discovery at the boundary to `t4_prep_adapter()`, SGE/TP parameter initialization, port-info initialization, adapter shutdown, BAR2 queue register mapping, devlog setup, CIM/TP debug readers, config/boot flashing, scheduler and SGE context reads, I2C access, VLAN ACLs, and other later helper APIs. Merge with later chunks should preserve that this range owns the mailbox engine, firmware/flash upgrade path, slow interrupt handling, link reply processing, RSS/TP/stat primitives, and VI/filter/queue command wrappers.
