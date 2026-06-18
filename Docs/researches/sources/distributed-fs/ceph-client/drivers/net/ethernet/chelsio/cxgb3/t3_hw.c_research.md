# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/t3_hw.c

## Purpose

`t3_hw.c` is the Chelsio T3 hardware bring-up, configuration, firmware/flash, PHY/MAC, interrupt, memory, and SGE-context programming implementation. It contains the low-level register sequences used by `cxgb3_main.c`, `sge.c`, PHY drivers, MAC code, and offload modules to prepare the adapter after reset and to operate slow-path hardware features. It is the main glue between generic driver state (`struct adapter`) and the register map in `regs.h`.

## Important APIs, Types, and Functions

- Register helpers: `t3_wait_op_done_val()`, `t3_write_regs()`, `t3_set_reg_field()`, and `t3_read_indirect()` provide polling, batch writes, masked updates, and indirect register reads.
- MDIO/PHY helpers: `t3_mdio_change_bits()`, `t3_phy_reset()`, `t3_phy_advertise()`, `t3_phy_advertise_fiber()`, `t3_set_phy_speed_duplex()`, LASI interrupt helpers, `t3_link_start()`, `t3_link_changed()`, and `t3_link_fault()` manage link configuration and state propagation.
- Adapter metadata: `t3_get_adapter_info()`, `get_vpd_params()`, `get_pci_mode()`, `init_link_config()`, and `t3_prep_adapter()` derive capabilities, VPD clocks/MAC addresses/port types, PCI mode, memory sizes, and software defaults.
- Flash/firmware/SRAM: `t3_seeprom_wp()`, `t3_get_fw_version()`, `t3_check_fw_version()`, `t3_load_fw()`, `t3_get_tp_version()`, `t3_check_tpsram_version()`, `t3_check_tpsram()`, and `t3_set_proto_sram()` validate or update firmware and protocol SRAM images.
- Interrupts: `t3_intr_enable()`, `t3_intr_disable()`, `t3_intr_clear()`, `t3_slow_intr_handler()`, module-specific interrupt handlers, and port interrupt helpers configure and dispatch non-data hardware events.
- SGE contexts: `t3_sge_init_ecntxt()`, `t3_sge_init_flcntxt()`, `t3_sge_init_rspcntxt()`, `t3_sge_init_cqcntxt()`, disable/enable helpers, and `t3_sge_cqcntxt_op()` write SGE internal context memory.
- Hardware init: `t3_reset_adapter()`, `t3_init_hw()`, `t3_replay_prep_adapter()`, `partition_mem()`, `tp_init()`, `tp_config()`, `ulp_config()`, `mc7_init()`, `chan_init_hw()`, `calibrate_xgm*()`, and `config_pcie()` perform reset-time sequencing.

## Control Flow

The preparation path starts in `t3_prep_adapter()`: it reads PCI mode and VPD, optionally resets the adapter, prepares SGE software defaults, computes TP/MC7 memory parameters when offload memory is present, initializes MC5/offload defaults, runs early hardware setup, clears parity-sensitive contexts/state, then prepares each port's PHY and MAC and assigns derived MAC addresses.

The full hardware initialization path in `t3_init_hw()` performs MAC calibration, partitions adapter memory, initializes MC7 memories and MC5, clears CQ contexts, initializes TP, configures Rx coalescing and max receive sizes, lays out ULP memory windows, configures PCIe/PCI-X behavior, sets PM and channel registers, calls `t3_sge_init()` for global SGE registers, enables fatal parity behavior, sets GPIO interrupt polarity, writes boot parameters for the on-card processor, then waits for firmware/uP initialization to clear `A_CIM_HOST_ACC_DATA`.

Slow interrupts enter through `t3_slow_intr_handler()`, which reads the top-level PL cause register, masks it by `slow_intr_mask`, dispatches to module handlers such as PCI/PCIe, SGE, MC7, CIM, TP, ULP, PM, CPL switch, MPS, MC5, MAC, or external GPIO handlers, then clears the processed top-level causes. Module handlers use the `intr_info` table model to warn, alert, increment stats, and invoke `t3_fatal_err()` on fatal causes.

SGE context initialization writes context data registers and invokes `t3_sge_write_context()`. It enforces 4 KiB-aligned base addresses, checks `F_CONTEXT_CMD_BUSY`, splits base addresses across context words, sets generation bits and validity, and masks sensitive response-queue bits that hardware cannot safely rewrite after reset.

## State and Persistence Behavior

Persistent hardware state includes EEPROM/VPD fields, serial flash firmware, TP SRAM, SGE context memory, memory-controller configuration, interrupt masks, MAC/PHY state, PCIe tuning registers, and adapter memory partitioning. Driver runtime state is stored in `adapter->params`, `adapter->irq_stats`, `mc7` statistics, `link_config`, PHY/MAC structs, and `slow_intr_mask`. Firmware updates are persistent across resets because `t3_load_fw()` erases and writes serial flash; most other register programming must be replayed after reset or recovery.

## Dependencies and Integration Points

The file depends on `common.h`, `regs.h`, `sge_defs.h`, and `firmware_exports.h`, plus Linux PCI, MDIO, netdev, sleep/polling, and byte conversion APIs. It integrates with PHY-specific prep functions (`ael1002`, `vsc8211`, `aq100x`, etc.), MAC functions (`xgmac.c`), MC5 functions (`mc5.c`), SGE queue setup (`sge.c`), the OS callbacks in `cxgb3_main.c`, offload logic, and firmware images/version definitions.

## Risks and Edge Cases

- Hardware sequencing is strict: reset, memory partitioning, MC7/MC5 init, TP init, ULP layout, SGE init, and firmware boot handoff must occur in the intended order.
- Poll loops return `-EAGAIN`, `-EBUSY`, `-EIO`, or `-EINVAL`; callers must not ignore these because subsequent register programming may target unready hardware.
- Flash writes validate checksums and read back written pages, but interruption during erase/write can leave firmware invalid.
- VPD parsing assumes specific EEPROM layout and hex/string encodings; malformed VPD can break clock, port type, and MAC setup.
- Interrupt masks differ by chip revision and PCI type. Incorrect fatal classification can either panic/reset too aggressively or miss unrecoverable parity/framing errors.
- SGE context writes are globally serialized by caller-side locking in some paths; concurrent context commands can collide if `reg_lock` discipline is bypassed.

## Test Signals

Strong signals include successful adapter prep/init across T3A/T3B/T3C and PCIe/PCI-X variants, correct VPD-derived MAC addresses and port types, link up/down and link-fault callbacks, firmware/version mismatch handling, flash update failure injection, MC7 BIST and interrupt stats, SGE context creation/disable under qset allocation/free, RSS table programming, interrupt enable/clear idempotence, and reset/replay recovery.
