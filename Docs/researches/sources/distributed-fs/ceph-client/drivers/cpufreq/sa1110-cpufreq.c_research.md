<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sa1110-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sa1110-cpufreq.c

## Purpose

Implements SA1110 CPU frequency scaling with SDRAM timing recalculation. It handles memory refresh/timing programming during PPCR clock changes for known SDRAM parts.

## APIs, Types, And Functions

`struct sdram_params` describes SDRAM timing, and `struct sdram_info` holds computed MDCNFG/MDREFR/MDCAS values. `sdram_calculate_timing()`, `sdram_update_refresh()`, and `sdram_set_refresh()` compute and apply memory timings. `sa1110_target()` performs the actual clock transition. `sa1110_find_sdram()` selects a timing profile from the module parameter or machine defaults.

## Control Flow

Arch init checks for SA1110, chooses SDRAM type from `cpu_sa1110.sdram=` or machine defaults, copies timing parameters, and registers cpufreq. CPU init installs the shared `sa11x0_freq_table`. Targeting calculates new SDRAM timings for the selected frequency, temporarily sets aggressive refresh, waits, disables interrupts, executes an aligned inline assembly block to program memory controller registers and PPCR without SDRAM accesses, restores interrupts, then updates refresh for the new frequency.

## State And Persistence

Global `sdram_params` stores selected memory timing. Hardware state persists in MDCNFG, MDREFR, MDCAS0-2, and PPCR. There is no module exit path because registration happens through `arch_initcall`.

## Dependencies And Integration Points

Depends on SA1100 machine headers, `sa11x0_freq_table`, `sa11x0_getspeed`, CPU revision checks, machine ID helpers, and direct memory controller registers.

## Risks And Test Signals

Incorrect SDRAM part selection can corrupt memory during transitions. The driver refuses no explicit unsupported SDRAM name by simply not registering. Test signals include selected SDRAM timing debug, CPU revision behavior for delayed latching, refresh counter values, successful transitions across table entries, and memory integrity under stress after frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sa1110-cpufreq.c -->
