<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.c -->
# sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.c

## Purpose
`core.c` implements common DWC2 controller services used by host and gadget modes: global register backup/restore, partial power down and hibernation coordination, core reset, mode forcing, active clock gating, register dump helpers, FIFO flushing, controller liveness checks, global interrupt enable/disable, hardware capability checks, polling helpers, host clock selection, and PHY initialization.

## Important APIs, types, and functions
Key functions are `dwc2_backup_global_registers`, `dwc2_restore_global_registers`, `dwc2_enter_partial_power_down`, `dwc2_exit_partial_power_down`, `dwc2_hib_restore_common`, `dwc2_enter_hibernation`, `dwc2_exit_hibernation`, `dwc2_core_reset`, `dwc2_force_mode`, `dwc2_force_dr_mode`, `dwc2_enable_acg`, `dwc2_flush_tx_fifo`, `dwc2_flush_rx_fifo`, `dwc2_is_controller_alive`, `dwc2_enable_global_interrupts`, `dwc2_disable_global_interrupts`, `dwc2_op_mode`, `dwc2_hw_is_otg`, `dwc2_hw_is_host`, `dwc2_hw_is_device`, wait-bit helpers, `dwc2_init_fs_ls_pclk_sel`, and `dwc2_phy_init`.

## Control flow
Power-state wrappers dispatch to host or gadget implementations based on current mode or backed-up `GOTGCTL_CURMODE_HOST`. Hibernation restore sequences toggle `GPWRDN` power/reset/clamp/restore bits, restore essential global and mode-specific registers, and poll for `GINTSTS_RESTOREDONE`. Core reset writes `GRSTCTL_CSFTRST`, waits using revision-specific completion semantics, clears gadget FIFO mapping, waits for AHB idle, and optionally waits for host mode after IDDIG debounce. Mode forcing edits `GUSBCFG_FORCEHOSTMODE` or `GUSBCFG_FORCEDEVMODE` only when hardware and requested `dr_mode` allow it. PHY init selects FS or HS setup, programs `GUSBCFG`, may reset after PHY changes, configures UTMI/ULPI details, sets turnaround timing, ULPI FS/LS bits, and host VBUS override behavior.

## State and persistence behavior
The file writes hardware registers and in-memory backups in `hsotg->gr_backup`, plus mode and parameter-derived runtime behavior. Backup validity is tracked with `gr_backup.valid` and consumed on restore. It also modifies `fifo_map` through `dwc2_clear_fifo_map` when gadget-capable builds reset the core. No disk persistence is involved; correctness depends on the controller retaining or losing register state according to the selected low-power mode.

## Dependencies and integration points
It depends on `core.h`, `hcd.h`, register definitions in `hw.h`, Linux delay/io/USB/HCD APIs, and host/gadget functions declared conditionally in `core.h`. It is called by platform probe, host init, gadget init, suspend/resume, interrupt handlers, and role-switch code.

## Risks
Register restore sequences are revision- and mode-sensitive; a wrong delay or missing valid backup can leave the core wedged. Reset polling uses microsecond loops and returns `-EBUSY` on timeout, so callers must handle failed hardware reset. Mode forcing can conflict with fixed `dr_mode`, and debounce delays can create races around role changes. PHY initialization has many SoC-specific flags, so regressions can break only certain UTMI/ULPI/FS combinations.

## Test signals
Useful tests include host/gadget/dual-role enumeration after reset, suspend/resume under partial power down and hibernation, controller revision coverage before and after 4.20a reset semantics, UTMI 8/16-bit and ULPI DDR/SDR configurations, low/full/high speed devices, FIFO flush timeout logs, `GSNPSID == 0xffffffff` dead-controller detection, and role switching with IDDIG debounce enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/dwc2/core.c -->
