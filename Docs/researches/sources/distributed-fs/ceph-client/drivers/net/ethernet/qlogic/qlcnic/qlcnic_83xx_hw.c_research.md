# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_83xx_hw.c

## Purpose

`qlcnic_83xx_hw.c` implements the 83xx/84xx hardware-specific side of the qlcnic driver. It installs the 83xx hardware and NIC operation tables, handles indirect register access, interrupt setup, mailbox command processing, asynchronous firmware events, RX/TX context creation, diagnostics, LED/link/pause/RSS/LRO/MAC/IP configuration, PCI/NIC information queries, flash read/write/erase helpers, driver lock recovery, memory writes, statistics, firmware minidump capability extension, shutdown/resume, mailbox workqueue lifecycle, and PCI AER callbacks.

The file is the concrete implementation behind many `struct qlcnic_hardware_ops` and `struct qlcnic_nic_template` callbacks declared in `qlcnic.h` and `qlcnic_83xx_hw.h`.

## Important APIs, Functions, And Data

Operation tables and register maps:

- `qlcnic_83xx_mbx_tbl[]`: mailbox command metadata mapping opcodes to input/output register counts.
- `qlcnic_83xx_ext_reg_tbl[]` and `qlcnic_83xx_reg_tbl[]`: indexed register tables used by shared register access and ethtool register dumps.
- `qlcnic_83xx_hw_ops`: supplies 83xx implementations for register access, mailbox commands, context create/destroy, link events, NIC/PCI info, MAC/VLAN changes, NAPI control, coalescing/RSS/LRO/promisc, PCI error callbacks, interrupt mask helpers, minidump helpers, and encapsulation offload checks.
- `qlcnic_83xx_ops`: higher-level NIC template for reset requests, IDC cancellation, NAPI add/del, IP address config, legacy interrupt clear, shutdown, and resume.
- `qlcnic_83xx_register_map()`: installs operation table and register table pointers in the hardware context.

Register and interrupt handling:

- `qlcnic_83xx_rd_reg_indirect()` and `qlcnic_83xx_wrt_reg_indirect()` program the per-function CRB window and read/write the wildcard register.
- `qlcnic_83xx_setup_intr()` chooses MSI-X/TSS-RSS/legacy INTx, allocates `intr_tbl`, rejects legacy INTx for function numbers above the supported range, and initializes interrupt descriptors.
- `qlcnic_83xx_clear_legacy_intr()`, `qlcnic_83xx_intr()`, `qlcnic_83xx_tmp_intr()`, `qlcnic_83xx_setup_mbx_intr()`, `qlcnic_83xx_free_mbx_intr()`, `qlcnic_83xx_enable_mbx_interrupt()`, and `qlcnic_83xx_disable_mbx_intr()` manage legacy/MSI-X interrupt acknowledgement, mailbox/AEN interrupt source routing, diagnostic interrupts, and NAPI scheduling.

Mailbox and AEN handling:

- `qlcnic_83xx_alloc_mbx_args()` allocates request/response arrays based on `qlcnic_83xx_mbx_tbl` and encodes HAL version in the command header.
- `qlcnic_83xx_issue_cmd()` queues mailbox commands and waits by completion, no-wait return, or busy polling depending on `cmd->type`.
- `qlcnic_83xx_init_mailbox_work()`, `qlcnic_83xx_detach_mailbox_work()`, `qlcnic_83xx_free_mailbox()`, `qlcnic_83xx_mailbox_worker()`, and `qlcnic_83xx_mbx_ops` implement the asynchronous mailbox queue.
- `__qlcnic_83xx_process_aen()`, `qlcnic_83xx_process_aen()`, `qlcnic_83xx_poll_process_aen()`, `qlcnic_83xx_handle_aen()`, and `qlcnic_83xx_mbx_poll_work()` parse firmware mailbox ownership, route link/IDC/request/time-extend/broadcast/SFP/DCB events, and notify mailbox completions.
- `qlcnic_dump_mbx()` and `qlcnic_dump_mailbox_registers()` provide failure diagnostics.

Context and queue programming:

- `qlcnic_83xx_create_rx_ctx()` builds `QLCNIC_CMD_CREATE_RX_CTX` with SDS/RDS mailbox payloads, programs status and receive ring DMA addresses, receives firmware context IDs and producer/consumer MMIO offsets, and optionally adds extra SDS rings through `qlcnic_83xx_add_rings()`.
- `qlcnic_83xx_del_rx_ctx()` destroys the RX context and marks it freed.
- `qlcnic_83xx_create_tx_ctx()` resets TX producer/consumer state, builds `struct qlcnic_tx_mbx`, selects interrupt IDs, sends `QLCNIC_CMD_CREATE_TX_CTX`, and stores firmware producer CRB and context ID.
- `qlcnic_83xx_del_tx_ctx()` destroys a TX context.

Configuration and management:

- `qlcnic_83xx_check_vf()` determines PCI function number, SR-IOV VF status, non-privileged function mode, and selects VF or 83xx NIC ops.
- `qlcnic_83xx_get_fw_version()`, `qlcnic_83xx_get_port_info()`, `qlcnic_83xx_get_port_config()`, `qlcnic_83xx_set_port_config()`.
- `qlcnic_83xx_initialize_nic()` registers or unregisters the NIC function with firmware and requests firmware resources plus loopback IDC/DCB AEN registration.
- `qlcnic_83xx_setup_link_event()`, `qlcnic_83xx_handle_link_aen()`, `qlcnic_83xx_test_link()`, `qlcnic_83xx_get_link_ksettings()`, and `qlcnic_83xx_set_link_ksettings()`.
- `qlcnic_83xx_get_pauseparam()` and `qlcnic_83xx_set_pauseparam()`.
- `qlcnic_83xx_config_led()`, `qlcnic_83xx_set_led()`, and `qlcnic_83xx_get_beacon_state()`.
- `qlcnic_83xx_nic_set_promisc()`, `qlcnic_83xx_sre_macaddr_change()`, `qlcnic_83xx_change_l2_filter()`, `qlcnic_83xx_get_mac_address()`, and `qlcnic_83xx_config_ipaddr()`.
- `qlcnic_83xx_config_hw_lro()`, `qlcnic_83xx_config_rss()`, `qlcnic_83xx_config_intr_coal()`, `qlcnic_83xx_set_rx_tx_intr_coal()`.
- `qlcnic_83xx_get_nic_info()`, `qlcnic_83xx_set_nic_info()`, `qlcnic_83xx_get_pci_info()`, and `qlcnic_get_pci_func_type()`.
- `qlcnic_83xx_config_intrpt()` adds/removes firmware interrupt registrations and stores firmware-provided source offsets.

Diagnostics and statistics:

- `qlcnic_83xx_diag_alloc_res()` and `qlcnic_83xx_diag_free_res()` temporarily detach normal netdev resources, create diagnostic contexts, post RX buffers, and restore prior ring counts/state.
- `qlcnic_83xx_loopback_test()`, `qlcnic_83xx_set_lb_mode()`, `qlcnic_83xx_clear_lb_mode()`, and `qlcnic_extend_lb_idc_cmpltn_wait()` run internal/external loopback with IDC completion AEN synchronization.
- `qlcnic_83xx_interrupt_test()` triggers a firmware interrupt test and checks `diag_cnt`.
- `qlcnic_83xx_reg_test()`, `qlcnic_83xx_get_regs_len()`, `qlcnic_83xx_get_registers()`.
- `qlcnic_83xx_get_stats()`, `qlcnic_83xx_fill_stats()`, and `qlcnic_83xx_copy_stats()` gather TX, MAC/eSwitch, and RX statistics through mailbox responses.

Flash, driver lock, and memory helpers:

- `qlcnic_83xx_lock_flash()` and `qlcnic_83xx_unlock_flash()` serialize flash operations with firmware/shared registers.
- `qlcnic_83xx_lockless_flash_read32()`, `qlcnic_83xx_flash_read32()`, `qlcnic_83xx_read_flash_descriptor_table()`, and `qlcnic_83xx_read_flash_mfg_id()`.
- `qlcnic_83xx_enable_flash_write()`, `qlcnic_83xx_disable_flash_write()`, `qlcnic_83xx_erase_flash_sector()`, `qlcnic_83xx_flash_write32()`, `qlcnic_83xx_flash_bulk_write()`, `qlcnic_83xx_flash_test()`, and `qlcnic_83xx_read_flash_status_reg()`.
- `qlcnic_83xx_lock_driver()`, `qlcnic_83xx_unlock_driver()`, and `qlcnic_83xx_recover_driver_lock()` coordinate multi-function driver locking and forced stale-lock recovery.
- `qlcnic_ms_mem_write128()` writes 128-bit chunks to QDR/DDR memory through indirect memory-space registers with alignment/range checks.

Power/error recovery:

- `qlcnic_83xx_shutdown()` detaches the netdev, cancels IDC work, brings the device down if running, disables mailbox interrupts, and saves PCI state.
- `qlcnic_83xx_resume()` reinitializes IDC, handles vNIC mode, reattaches the driver, and schedules IDC polling.
- `qlcnic_83xx_io_error_detected()`, `qlcnic_83xx_io_slot_reset()`, and `qlcnic_83xx_io_resume()` implement PCI AER handling.

## Control Flow And State Behavior

Probe/hardware selection flow:

1. `qlcnic_83xx_register_map()` installs 83xx operation tables and register maps.
2. `qlcnic_83xx_check_vf()` reads the function number and op mode, selects VF ops for SR-IOV VFs or non-privileged functions, and marks SR-IOV capability for privileged PFs.
3. Firmware version, PCI info, NIC info, port config, and capabilities are read through shared registers and mailbox commands.

Open/context flow:

1. Interrupt setup allocates `ahw->intr_tbl`, chooses MSI-X or legacy fallback, and assigns type/id/source placeholders.
2. Firmware interrupt registration through `qlcnic_83xx_config_intrpt()` fills source offsets.
3. `qlcnic_83xx_create_rx_ctx()` and `qlcnic_83xx_create_tx_ctx()` create firmware contexts and bind hardware CRB producer/consumer pointers to ring structures.
4. NAPI and interrupt enable callbacks then drive RX/TX completion processing elsewhere in the driver.

Mailbox flow:

1. Callers allocate `qlcnic_cmd_args` using metadata-derived register counts.
2. `qlcnic_83xx_issue_cmd()` enqueues the command and selects wait/no-wait/busy-wait semantics.
3. The mailbox worker serializes commands, writes host mailbox registers, sets host ownership, waits for completion signaled by an interrupt or poll path, decodes firmware status, clears ownership, and dequeues.
4. A timeout marks the mailbox not ready, dumps registers, captures mailbox data, requests a firmware dump/reset, and returns timeout status.
5. AEN paths share the same firmware mailbox space and are protected by `aen_lock`.

Configuration flow:

- Link, pause, LED, loopback, RSS, LRO, coalescing, promisc, MAC/VLAN, IP, and NIC info changes generally build one mailbox command, encode context/function identity in `arg[1]`, issue it, and update local `ahw`/adapter state only on success or restore old state on failure.
- Loopback is special: it tears down normal resources, creates diagnostic resources, sets port loopback mode, waits for IDC completion and link-up AENs, sends loopback traffic, clears loopback mode, and restores normal resources.

Flash and persistent state flow:

- Flash operations lock the flash semaphore, program flash direct-window/control/data registers, poll `QLC_83XX_FLASH_STATUS_READY`, and unlock.
- Flash descriptor table and manufacturer ID are cached in `adapter->ahw->fdt` and `adapter->flash_mfg_id`.
- Writes and erases may enable/disable flash write based on FDT manufacturer matching.

Stateful fields include `adapter->flags`, `adapter->state`, `recv_ctx->state`, ring producer/consumer indexes, `ahw->intr_tbl`, `ahw->mailbox`, `ahw->mbox_aen`, `ahw->idc.status`, `ahw->port_config`, `ahw->link_*`, `ahw->beacon_state`, `ahw->fdt`, `adapter->flash_mfg_id`, `ahw->diag_test`, `ahw->diag_cnt`, and temporary LED mailbox register snapshots.

## Dependencies And Integration Points

This file integrates with:

- `qlcnic.h` for adapter/hardware context types, operation-table definitions, common wrappers, and shared constants.
- `qlcnic_83xx_hw.h` for 83xx register offsets, mailbox structs, IDC state, flash constants, and prototypes.
- `qlcnic_sriov.h` for PF/VF interface IDs and broadcast event handling.
- Common qlcnic modules for attach/detach, up/down, context orchestration, RX buffer posting, loopback traffic, firmware dump/reset, IDC state machine, vNIC operation, sysfs, minidump, ethtool, DCB, and SR-IOV.
- Linux PCI error recovery, IRQ registration, MSI-X, workqueues, completions, spinlocks, netdev, ethtool link settings, firmware, and MMIO accessors.

## Risks And Edge Cases

- Mailbox/AEN concurrency is delicate because command completions and async events share firmware mailbox registers. Incorrect ownership clearing or locking can lose events or hang commands.
- `qlcnic_83xx_nic_set_promisc()` and `qlcnic_83xx_sre_macaddr_change()` intentionally return before freeing no-wait command memory on successful queueing; completion cleanup happens later in `qlcnic_83xx_notify_cmd_completion()`. Changing this pattern can double-free or leak.
- Interrupt setup allocates `intr_tbl`; the legacy path returns `-EOPNOTSUPP` for unsupported functions after allocation without freeing in this function, so callers must clean up on failure.
- RX/TX context creation relies on hard-coded mailbox argument offsets and packed structs. Off-by-one register counts corrupt firmware payloads.
- `qlcnic_83xx_create_rx_ctx()` computes `num_sds = adapter->drv_sds_rings - QLCNIC_MAX_SDS_RINGS` in `qlcnic_83xx_add_rings()`; callers must only enter this path when more than the base number of SDS rings exists.
- Diagnostic paths detach/re-attach resources and manipulate ring counts. Failures must restore `drv_sds_rings`, `drv_tx_rings`, `diag_test`, and netdev attachment state.
- Loopback waits depend on AEN delivery and may extend wait time from firmware events. Missing AENs yield timeouts and must clear mode safely.
- Flash functions cast byte pointers to `u32 *` and require 4-byte aligned addresses/counts. Unaligned buffers or counts can fault or corrupt reads.
- Flash erase address byte reversal and OEM/FDT command selection are hardware-specific and easy to break.
- Driver lock recovery force-unlocks stale owners across functions. Incorrect owner detection could break another live function.
- Link setting code maps legacy supported/advertising bits into modern ethtool structures; unsupported half-duplex and autoneg behavior differs by port type.
- AER paths disable PCI and stop polling; reattach failures must leave reset/AER bits consistent.

## Test Signals

High-value validation includes:

- 83xx probe/open/close/remove with MSI-X, MSI, and legacy INTx fallback.
- Mailbox command tests for every metadata entry touched by changes, including timeout injection and AEN interleaving.
- RX/TX context creation/destruction with single ring, multiple SDS/TX rings, RSS/TSS, and loopback diagnostic contexts.
- Link up/down, SFP insert/remove, DCB config-change AEN, IDC request/completion, and broadcast event tests.
- Etthtool coverage: LED identify, link settings get/set, pauseparam get/set, coalescing, register dump, interrupt test, loopback test, flash test, and statistics.
- SR-IOV PF/VF and non-privileged function testing for operation gating and interface ID encoding.
- Flash read/FDT/mfg-id paths on supported hardware, plus write/erase tests only under controlled conditions.
- Suspend/resume and PCI AER recovery with firmware reset/dump paths enabled.
- Lockdep, KASAN, DMA API debug, sparse endian checks, and fault injection for allocation failures and mailbox timeouts.
