# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/drvfbi.c

## Purpose
`drvfbi.c` is the board-dependent FBI glue for SMT and LLC. It resets and starts/stops PCI FDDI hardware, reads board identity and MAC address data, handles top-level MAC/PLC/timer interrupt entry points, controls the optical bypass, updates LEDs, and bridges protocol-state changes to OS or driver callbacks.

## Important APIs, Types, And Functions
Key entry points are `init_board()`, `card_stop()`, `read_address()`, `mac1_irq()`, `plc1_irq()`, `plc2_irq()`, `timer_irq()`, `sm_pm_bypass_req()`, `sm_pm_bypass_present()`, `pcm_state_change()`, `rmt_indication()`, `driver_get_bia()`, and `smt_start_watchdog()`. `card_start()` and `smt_stop_watchdog()` are internal reset helpers. Optional `set_oi_id_def()` validates the MULT_OEM ID table.

## Control Flow
`init_board()` calls `card_start()`, reads MAC/PMD metadata, then sets SAS/DAS and bypass-present MIB state from `B0_DAS`. `card_start()` stops the watchdog, quiesces FORMAC, resets HPI/master/chips, clears PCI status errors, detects 64-bit-capable board revisions, initializes BMU watermarks, LED state, watchdog interval, interrupt mask, and `hw_state`. `card_stop()` performs the quiesce/reset path and clears LEDs.

Interrupt dispatch is thin: `mac1_irq()` handles FORMAC status-1 transmit/parity/underrun conditions and restarts transmit paths; `plc1_irq()`/`plc2_irq()` read PLC interrupt status and call `plc_irq()` for B/A respectively; `timer_irq()` restarts the hardware timer and drains SMT timers. LED updates follow PCM active states and RMT ring-up indications.

## State And Persistence
Runtime state lives in `smc->hw` (`hw_state`, `is_imask`, `hw_is_64bit`, MAC addresses, watchdog use, ring-up flag) plus MIB fields for bypass presence and station type. It reads board PROM/config registers but does not persist changes across resets except hardware latch state such as bypass insert/remove and LED/watchdog registers.

## Dependencies And Integration Points
The file depends on `skfbiinc.h`, `supern_2.h`, `skfbi.h` register macros, Linux PCI and bit reversal helpers, FORMAC helpers (`formac_tx_restart()`), PLC handling (`plc_irq()`), SMT timer code, LLC restart callbacks, and optional driver hooks `DRV_PCM_STATE_CHANGE`/`DRV_RMT_INDICATION`.

## Risks And Edge Cases
Reset order is hardware-sensitive: FORMAC init, HPI reset, PCI status clearing, and BMU watermarks are sequenced deliberately. MAC addresses are stored in both FDDI physical bit order and canonical order; wrong bit reversal breaks address matching. `mac1_irq()` loops after restart until status clears, so unhandled sticky bits can spin. `sm_pm_bypass_present()` reads hardware directly and assumes PCI register access is valid.

## Test Signals
Validate cold init and stop, SAS versus DAS detection, optional bypass insert/deinsert, watchdog start/stop, physical and canonical MAC address reads, green/yellow LED changes during PCM/RMT transitions, transmit abort recovery calling `llc_restart_tx()`, parity/underrun panic paths, PLC interrupt routing, timer interrupt draining SMT timers, and MULT_OEM table validation when enabled.
