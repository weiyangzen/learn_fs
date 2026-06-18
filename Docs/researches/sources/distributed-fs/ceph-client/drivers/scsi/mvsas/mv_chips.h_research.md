# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/mv_chips.h

Purpose: provides generic inline register-access and common hardware helper routines shared by the 64xx and 94xx mvsas chip implementations. It abstracts per-port register windows, command indirect registers, interrupt draining, delivery/completion ring pointers, PRD sizing, PCIe link reporting, and max link-rate reporting.

Important APIs/types/functions: macros `mr32`, `mw32`, and `mw32_f` wrap MMIO access through a local `regs` variable; `iow*/ior*` wrap port-I/O style access. Helpers include `mvs_cr32()`, `mvs_cw32()`, per-phy/per-port config/VSR/IRQ accessors, `mvs_phy_hacks()`, `mvs_int_sata()`, `mvs_int_full()`, `mvs_start_delivery()`, `mvs_rx_update()`, `mvs_get_prd_size()`, `mvs_get_prd_count()`, `mvs_show_pcie_usage()`, and `mvs_hw_max_link_rate()`.

Control flow: per-chip files include their register header before this header, so the inline functions compile against the correct offsets and `struct mvs_prd` shape. Interrupt flow in `mvs_int_full()` reads central status, drains RX completions, dispatches per-port events, handles non-specific NCQ and SRS interrupts, and acknowledges central status.

State and persistence: operates on `struct mvs_info` runtime state and hardware registers. No persistent storage is modified directly.

Dependencies and integration points: depends on `mv_sas.h` types, per-chip register constants, common interrupt functions from `mv_sas.c`, and `MVS_CHIP_DISP` dispatch callbacks. Used by both `mv_64xx.c` and `mv_94xx.c`.

Risks and test signals: macros require a correctly named local `regs` variable, so misuse can compile incorrectly or not at all. Port-I/O helper casts are unusual and deserve architecture coverage. Interrupt helper behavior depends on per-chip `non_spec_ncq_error` and `clear_active_cmds` hooks. Tests should include both chip families, interrupt storm handling, SRS interrupts, PCIe status display, and sparse/build checks for MMIO annotations.
