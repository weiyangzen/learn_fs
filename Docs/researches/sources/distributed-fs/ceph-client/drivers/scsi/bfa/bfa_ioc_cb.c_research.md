<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_cb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_cb.c

## Purpose
`bfa_ioc_cb.c` supplies the Crossbow/CB ASIC-specific implementation of the generic IOC hardware-interface table. It maps PCI function and port registers, checks firmware compatibility for multi-function coexistence, drives per-port firmware-state scratch registers, handles synchronized IOC failure cleanup through join bits, and initializes the CB PLL/reset state.

## Important APIs, Types, And Functions
The exported entry points are `bfa_ioc_set_cb_hwif()` and `bfa_ioc_cb_pll_init()`. `bfa_ioc_set_cb_hwif()` populates the static `hwif_cb` `struct bfa_ioc_hwif_s` with CB-specific callbacks. Internal callbacks include `bfa_ioc_cb_firmware_lock()`, `bfa_ioc_cb_firmware_unlock()`, `bfa_ioc_cb_reg_init()`, `bfa_ioc_cb_map_port()`, `bfa_ioc_cb_isr_mode_set()`, `bfa_ioc_cb_notify_fail()`, `bfa_ioc_cb_ownership_reset()`, `bfa_ioc_cb_sync_start()`, `bfa_ioc_cb_sync_join()`, `bfa_ioc_cb_sync_leave()`, `bfa_ioc_cb_sync_ack()`, `bfa_ioc_cb_sync_complete()`, and current/alternate firmware-state get/set helpers.

Static register maps `iocreg_fnreg[]` and `iocreg_mbcmd[]` translate PCI functions 0 and 1 to host/LPU mailbox windows, command/status registers, and host page-number registers. `bfa_ioc_cb_join_pos()` and `BFA_IOC_CB_JOIN_MASK`-based operations preserve failure-join bits in the same registers that carry `BFI_IOC_*` firmware states.

## Control Flow
Attach-time flow calls `bfa_ioc_set_cb_hwif()`, then generic IOC code invokes `ioc_map_port()` and `ioc_reg_init()`. CB maps `port_id` directly from the PCI function, selects heartbeat/current/alternate firmware-state registers by port, and maps the mailbox, PSS, PLL, semaphore, SRAM-page, and error-notification registers from BAR0.

Firmware lock flow reads current and alternate firmware states. If the current state is `BFI_IOC_UNINIT`, this driver can initialize firmware. Otherwise it reads the running firmware header with `bfa_ioc_fwver_get()` and compares it with the driver image through `bfa_ioc_fwver_cmp()`. A mismatch blocks initialization unless the alternate IOC is disabled.

Failure synchronization flow stores join/ack state in the high bits of the firmware-state registers. `sync_start()` clears stale join bits left by an unclean prior driver exit, otherwise delegates to `sync_complete()`. `sync_join()` sets this IOC's join bit, `sync_leave()` clears it, `sync_ack()` marks the current state as `BFI_IOC_FAIL`, and `sync_complete()` allows reset/recovery when this IOC or the alternate IOC is in a safe state such as `UNINIT`, `INITING`, `DISABLED`, `MEMTEST`, `OP`, or `FAIL` depending on the path.

`bfa_ioc_cb_pll_init()` clears firmware states while preserving join bits, masks and clears host interrupts, pulses SCLK/LCLK soft-reset and bypass bits, programs PLL control values, waits with `udelay()`, clears pending interrupts again, and releases PLL logic reset. It returns `BFA_STATUS_OK`.

## State And Persistence
The file persists no kernel-owned long-term state beyond assigning `ioc->ioc_hwif` and filling `ioc->ioc_regs`. Persistent coordination is through hardware registers: per-IOC firmware-state registers, join bits, host semaphores, mailbox windows, interrupt mask/status registers, PLL control registers, and the error-set register. `bfa_ioc_cb_ownership_reset()` carefully reads the semaphore before writing `1` so it clears a held semaphore instead of accidentally acquiring an unlocked one.

## Dependencies And Integration Points
This file depends on `bfad_drv.h`, `bfa_ioc.h`, `bfi_reg.h`, and `bfa_defs.h` for kernel helpers, IOC definitions, and register offsets/bit masks. It integrates directly with the generic IOC by filling `struct bfa_ioc_hwif_s`, and with firmware compatibility logic through `bfa_ioc_fwver_get()` and `bfa_ioc_fwver_cmp()`. Hardware notification of heartbeat failure is emitted by writing all ones to `err_set`.

## Risks And Test Signals
Key risks include stale join bits blocking later driver loads, firmware-state writes clobbering join bits, incorrect PCI-function indexing into two-entry register maps, and PLL sequencing regressions that leave the ASIC or firmware in an unbootable state. `bfa_ioc_cb_isr_mode_set()` is intentionally empty, so generic callers must tolerate no-op interrupt-mode switching on CB.

Good test signals include CB attach on both PCI functions, firmware mismatch detection when another function is active, recovery after unclean driver unload with join bits set, heartbeat failure propagation through `ERR_SET_REG`, semaphore cleanup correctness, firmware boot after `bfa_ioc_cb_pll_init()`, and mailbox command/response operation on both function register maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_cb.c -->
