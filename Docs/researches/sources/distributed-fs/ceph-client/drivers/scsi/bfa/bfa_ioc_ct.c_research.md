<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_ct.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_ct.c

## Purpose
`bfa_ioc_ct.c` implements Catapult/CT and Catapult2/CT2 ASIC-specific IOC hardware-interface behavior. It handles firmware usage-count locking, firmware-state and failure-sync registers shared across functions, port and mailbox register mapping, interrupt-mode selection for CT, CT2 LPU read-status handling, CT2 MSI-X vector-table workaround, and PLL/clock/NFC/flash/MAC/memory reset sequences.

## Important APIs, Types, And Functions
The exported hardware-interface entry points are `bfa_ioc_set_ct_hwif()`, `bfa_ioc_set_ct2_hwif()`, `bfa_ioc_ct2_poweron()`, `bfa_ioc_ct_pll_init()`, and `bfa_ioc_ct2_pll_init()`. Shared CT-family callbacks include `bfa_ioc_ct_firmware_lock()`, `bfa_ioc_ct_firmware_unlock()`, `bfa_ioc_ct_notify_fail()`, `bfa_ioc_ct_ownership_reset()`, `bfa_ioc_ct_sync_start()`, `bfa_ioc_ct_sync_join()`, `bfa_ioc_ct_sync_leave()`, `bfa_ioc_ct_sync_ack()`, `bfa_ioc_ct_sync_complete()`, and firmware-state get/set helpers.

CT-specific helpers are `bfa_ioc_ct_reg_init()`, `bfa_ioc_ct_map_port()`, and `bfa_ioc_ct_isr_mode_set()`. CT2-specific helpers are `bfa_ioc_ct2_reg_init()`, `bfa_ioc_ct2_map_port()`, `bfa_ioc_ct2_lpu_read_stat()`, `bfa_ioc_ct2_sclk_init()`, `bfa_ioc_ct2_lclk_init()`, `bfa_ioc_ct2_mem_init()`, `bfa_ioc_ct2_mac_reset()`, `bfa_ioc_ct2_enable_flash()`, NFC halt/resume/wait helpers, `bfa_ioc_ct2_clk_reset()`, and `bfa_ioc_ct2_nfc_clk_reset()`.

Static tables `ct_fnreg[]`, `ct_p0reg[]`, `ct_p1reg[]`, and `ct2_reg[]` map PCI functions or logical ports to mailbox and command/status offsets. The `ioc_fail_sync` register is split into low acknowledge bits and high required bits via `bfa_ioc_ct_get_sync_ackd()`, `bfa_ioc_ct_get_sync_reqd()`, and `bfa_ioc_ct_sync_reqd_pos()`.

## Control Flow
Attach-time flow for CT calls `bfa_ioc_set_ct_hwif()`, which first fills shared CT-family operations through `bfa_ioc_set_ctx_hwif()` and then assigns CT PLL, register-init, port-map, and ISR-mode callbacks. CT maps port ID from the function-personality register and maps mailbox command/status to LPU0 or LPU1 depending on the resolved port. CT2 follows the same shared setup but uses CT2 register offsets, maps the port from `CT2_HOSTFN_PERSONALITY0`, installs `bfa_ioc_ct2_lpu_read_stat()`, and leaves `ioc_isr_mode_set` as `NULL`.

Firmware locking serializes on `ioc_usage_sem_reg`. If use count is zero, the first driver sets use count to one, releases the semaphore, clears failure-sync state, and can initialize firmware. If firmware is already in use, the code rejects mismatched firmware images and increments the use count only when `bfa_ioc_fwver_cmp()` succeeds. Unlock decrements the use count under the same semaphore and warns on invalid counts.

Failure synchronization uses `ioc_fail_sync`. `sync_join()` records that this function requires coordinated failure handling; `sync_ack()` records that this function has acknowledged failure; `sync_complete()` waits until required and acknowledged masks match, then clears acknowledged bits and writes `BFI_IOC_FAIL` to both current and alternate firmware states. It also handles a race where another function reinitialized and failed again while this IOC was waiting for the hardware semaphore by reasserting this function's ack bit.

CT PLL init programs FC or FCoE operating mode, resets firmware-state registers, masks/clears interrupts, enables SCLK/LCLK PLLs, optionally resets PMM for non-FC mode, releases LMEM reset, and runs EDRAM BIST. CT2 PLL init branches on WGN/NFC state: it may reset clocks directly, enable flash, reset MACs, wait for NFC firmware to run and ask it to reset PLLs, or halt NFC and perform manual clock/MAC reset. It also applies an ATC DMA-read workaround, masks mailbox interrupts, clears stale command status after prior initialization, initializes memory, and marks both CT2 IOC states uninitialized.

## State And Persistence
Persistent coordination is almost entirely in hardware registers: firmware use count, usage/init semaphores, failure-sync bitmaps, firmware-state registers, mailbox windows, LPU halt registers, personality registers, PLL controls, NFC status/control registers, flash GPIO controls, interrupt masks/status, and SRAM-page registers. Kernel-side state is the selected static hardware-interface table and register pointers stored in `ioc->ioc_regs`.

The use-count lock is a reference-counting contract across PCI functions sharing firmware. Failure-sync bits persist across unclean exits until `sync_start()` or ownership reset clears them. `bfa_ioc_ct2_poweron()` persists MSI-X vector count/offset defaults in host function vector-table registers when firmware/ASIC block configuration did not set them.

## Dependencies And Integration Points
The file depends on the same IOC and register headers as the CB implementation: `bfad_drv.h`, `bfa_ioc.h`, `bfi_reg.h`, and `bfa_defs.h`. It integrates with generic IOC state machines through `struct bfa_ioc_hwif_s`, with firmware-image validation through `bfa_ioc_fwver_get()`/`bfa_ioc_fwver_cmp()`, and with IOC personality through `bfa_ioc_is_cna()` and `bfa_ioc_pcifn()`. It is the chip-policy layer that lets generic mailbox, heartbeat, and boot code operate against CT/CT2 register layouts.

## Risks And Test Signals
Risks include use-count leaks on failed attach/detach, firmware mismatch handling races under the usage semaphore, failure-sync bit races across multiple PFs, incorrect CT port mapping from personality bits, CT2 register-table indexing by port rather than function, and PLL/NFC reset paths that depend on exact hardware status values. The CT2 ATC workaround and MSI-X vector workaround are hardware errata-sensitive and should not be reordered casually. Several waits use fixed `udelay()` polling with `WARN_ON()` rather than recoverable errors, so failures may surface as boot instability rather than clean status codes.

Good test signals include CT attach on PF0-PF3, CT2 attach on both ports, concurrent function firmware sharing with matching and mismatched images, use-count decrement on detach, failure recovery when one function fails while another is active, CT interrupt-mode switching between INTx/MSI-X, CT2 LPU read-status clearing, CT/CT2 firmware boot after PLL init in FC and FCoE/CNA modes, and recovery from stale `ioc_fail_sync` bits after an unclean prior unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_ioc_ct.c -->
