# sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu.c

## Purpose
`db8500-prcmu.c` is the central PRCMU firmware interface for ST-Ericsson DB8500/Ux500 platforms. It handles PRCMU MMIO, TCDM mailboxes, power-state transitions, wakeups, OPP changes, ePOD power domains, autonomous PM, clocks, PLLs, thermal/watchdog commands, ABB I2C proxying, modem wake/sleep/reset, PRCMU IRQ demultiplexing, firmware version discovery, regulator data, and MFD child registration.

## Important APIs, Types, and Functions
Low-level exports include `db8500_prcmu_read()`, `db8500_prcmu_write()`, `db8500_prcmu_write_masked()`, and `prcmu_get_fw_version()`. Power/OPP APIs include `prcmu_set_rc_a2p()`, `prcmu_get_rc_p2a()`, `prcmu_get_xp70_current_state()`, `db8500_prcmu_set_power_state()`, `db8500_prcmu_enable_wakeups()`, `db8500_prcmu_set_arm_opp()`, `db8500_prcmu_set_ape_opp()`, `db8500_prcmu_request_ape_opp_100_voltage()`, `db8500_prcmu_set_epod()`, and `prcmu_configure_auto_pm()`. Clock APIs include `db8500_prcmu_request_clock()`, `prcmu_clock_rate()`, `prcmu_round_clock_rate()`, and `prcmu_set_clock_rate()`. Firmware command APIs cover hotmon/temp sense, A9 watchdog, ABB reads/writes, AC wake/sleep, system reset, reset-code retrieval, and modem reset. `prcmu_irq_handler()`, mailbox readers, and `prcmu_irq_chip` implement IRQ demux. `db8500_prcmu_early_init()` maps PRCMU early and initializes synchronization; `db8500_prcmu_probe()` performs full platform registration.

## Control Flow
Early init finds the `stericsson,db8500-prcmu` node, maps PRCMU registers, reads firmware version from the second region, and initializes locks/completions/work. Platform probe remaps named PRCMU and TCDM resources with devm, clears pre-kernel mailbox interrupts, requests the PRCMU IRQ as threaded, creates the PRCMU irqdomain, configures ESRAM0 sleep retention, registers watchdog/cpuidle/regulator/thermal children, and registers the AB8500/AB8505 child found in the device tree. Most firmware requests wait for the target mailbox bit to become free, write request payloads into TCDM, set the CPU mailbox bit, and wait for a completion populated by the IRQ handler. Mailbox 0 wake events can return `IRQ_WAKE_THREAD`; the thread ACKs DBB wakeups with a follow-up mailbox message.

## State and Persistence
Global state includes `prcmu_base`, `tcdm_base`, firmware info, the PRCMU irqdomain, mailbox transfer structures with locks/completions/ack caches, wakeup/IRQ request masks, clock-management cached PLL switch bits, DSI divider selections, autonomous PM enabled state, and AC wake atomic state. Hardware state spans PRCMU registers and TCDM mailboxes. Reset reason is persisted only in PRCMU TCDM until overwritten or reset by firmware.

## Dependencies and Integration Points
The driver depends on OF resources/IRQs, Linux IRQ domains, threaded IRQs, MFD core, AB8500 MFD integration, regulator init data, Ux500 PRCMU public headers, and MMIO helpers. It is the backend for clock, cpufreq, regulator, thermal, watchdog, cpuidle, ABB, modem, and reset users on DB8500-family systems.

## Risks and Edge Cases
Many paths busy-wait on mailbox or hardware semaphore availability with `cpu_relax()` and no timeout, so firmware lockups can hang callers. Several APIs use `BUG_ON()` for invalid caller input, making misuse fatal. Early and probe-time mappings both assign global `prcmu_base`; ordering is critical. `db8500_irq_init()` return value is ignored in probe. `request_threaded_irq()` is not released on later MFD registration failures. AC wake/sleep and mailbox completions have long timeouts but limited recovery. `prcmu_irq_mask()` compares `d->irq` against a hardware IRQ index constant, which is suspicious because `d->irq` is a Linux virq while `d->hwirq` is the PRCMU index.

## Test Signals
Important signals include firmware version logging, mailbox IRQ completions for MB1/2/4/5, wakeup IRQ demux through the PRCMU domain, clock request/rate/round/set behavior for register clocks, DSI PLL lock failure paths, ARM/APE OPP transitions, ePOD timeout handling, ABB I2C proxy read/write status, AC wake/sleep completion, reset-code round trip, MFD child registration, and boot under each supported firmware project name.
