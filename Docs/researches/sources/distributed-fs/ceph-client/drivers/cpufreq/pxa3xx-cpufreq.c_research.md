<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa3xx-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pxa3xx-cpufreq.c

## Purpose

Provides PXA3xx CPU frequency scaling by programming ACCR core and bus clock fields for PXA300/PXA310/PXA320 operating points.

## APIs, Types, And Functions

`struct pxa3xx_freq_info` stores CPU MHz, ACCR field values, DFI divider, and voltage metadata. Static tables describe PXA300 and PXA320 points. `setup_freqs_table()` allocates a cpufreq table, `__update_core_freq()` updates XL/XN and XSPCLK fields through `pxa3xx_clk_update_accr()`, and `__update_bus_freq()` updates memory/static bus selectors.

## Control Flow

Init registers only on PXA3xx. Policy init sets fixed min/max, chooses PXA300/PXA310 or PXA320 table, and installs it. Targeting only accepts CPU0, disables local IRQs, updates core PLL fields, then bus frequency fields, and restores IRQs.

## State And Persistence

Global pointers retain the selected operating-point array and allocated cpufreq table. Hardware state persists in ACCR and related clock registers. Voltage fields are descriptive in this driver and are not applied through regulators.

## Dependencies And Integration Points

Depends on PXA CPU identification, PXA clock helper `pxa3xx_clk_update_accr()`, `pxa3xx_get_clk_frequency_khz()`, and cpufreq table APIs.

## Risks And Test Signals

Clock register sequencing is interrupt-protected but lacks regulator handling despite voltage data. The global allocated table is not freed on driver exit. Test signals include correct CPU family detection, ACCR field readback for every operating point, current frequency from PXA clock helper, and stable memory/static bus operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa3xx-cpufreq.c -->
