# sources/distributed-fs/ceph-client/drivers/clocksource/timer-microchip-pit64b.c

Purpose: Microchip SAM9X60 PIT64B driver using two DT instances: first for clockevent, second for 64-bit clocksource/sched_clock/delay timer.

Important APIs/types/functions: `struct mchp_pit64b_timer` captures base, pclk, gclk, and precomputed mode; wrapper structs embed clockevent or clocksource. `mchp_pit64b_init_mode()` chooses GCLK or PCLK and prescaler for a target 5 MHz. `mchp_pit64b_reset()` resets/programs period/mode/IRQ and starts. Clocksource and clockevent init allocate persistent wrappers.

Control flow: `mchp_pit64b_dt_init()` uses static `inits`; case 0 initializes event timer with IRQ, case 1 initializes clocksource without IRQ. Per timer init obtains clocks and MMIO, computes mode/rate, then registers either event or source. Clockevent callbacks resume clocks if needed and reset PIT in periodic/one-shot mode; shutdown suspends clocks unless detached. ISR reads status to clear then calls event handler.

State/persistence: global `mchp_pit64b_cs_base`, `mchp_pit64b_ce_cycles`, delay timer, static init count, and allocated wrappers persist. Suspend/resume callbacks gate pclk/gclk.

Dependencies/integration: compatible `microchip,sam9x60-pit64b`, named `pclk`/`gclk`, CCF rate setting, clocksource/clockevents/sched_clock/delay.

Risks: DT instance order determines role; clocksource read uses a global base rather than per-instance pointer; clock rate selection has hardware pclk/gclk constraints; partial errors dispose IRQ/unmap but may leak clocks. Tests should cover two-node DT order, clock-rate logs, suspend/resume, 64-bit read atomicity, and event IRQ clearing.
