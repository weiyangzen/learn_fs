# sources/distributed-fs/ceph-client/drivers/memory/jz4780-nemc.c

## Purpose
`jz4780-nemc.c` drives the Ingenic JZ4740/JZ4780 NAND/external memory controller. It configures static-memory bank timing and exposes helper APIs for child NAND/SRAM drivers to count banks, select bank type, and assert NAND chip enable.

## Important APIs, Types, And Functions
`struct jz4780_nemc` stores lock, device, SoC info, base, clock, calculated clock period, and banks-present bitmap. `struct jz_soc_info` supplies maximum tAS/tAH cycle counts per SoC.

Exported functions are `jz4780_nemc_num_banks()`, `jz4780_nemc_set_type()`, and `jz4780_nemc_assert()`. Timing helpers include `jz4780_nemc_clk_period()`, `jz4780_nemc_ns_to_cycles()`, and `jz4780_nemc_configure_bank()`. Probe requests only the used register prefix, maps it, clears `NEMC_NFCSR`, enables the clock, parses child address banks, rejects conflicts, configures bank timings, and creates child platform devices.

## Control Flow
Probe iterates available child nodes. For each child it scans `reg` entries via `of_get_address()`, validates bank numbers, checks conflicts with earlier children, applies timing properties to each referenced bank, and creates a child platform device if configuration succeeded. Invalid children are skipped rather than failing the whole controller.

## State And Persistence
Hardware state is SMCR timing/config registers and NFCSR NAND/SRAM/chip-enable state. Runtime state includes clock period and `banks_present`. The clock remains prepared while the driver is bound and is disabled on remove. Child helper calls directly mutate NFCSR.

## Dependencies And Integration Points
It integrates with OF child address parsing, platform child creation, clock framework, and exported `linux/jz4780-nemc.h` types. It registers at `subsys_initcall()` so child drivers can depend on it early.

## Risks
Only 8-bit bus width is accepted despite comments about older SoCs supporting 16-bit. Probe does not depopulate created children on remove. NFCSR helper writes are not protected by the declared spinlock, so concurrent child access can race. Timing conversion depends on a nonzero clock rate.

## Test Signals
Tests should verify invalid/duplicate bank rejection, timing overflow errors for tAS/tAH/tBP/tAW/tSTRV, child creation for valid banks, exported helper behavior, and removal clock disable. NAND tests should verify chip-enable toggling through NFCSR.
