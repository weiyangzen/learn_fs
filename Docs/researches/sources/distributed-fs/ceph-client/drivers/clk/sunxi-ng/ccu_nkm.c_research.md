# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_nkm.c

## Purpose
`ccu_nkm.c` implements the sunxi-ng common-clock-framework operations for N*K/M PLL clocks with optional parent-rate adjustment and hardware validity constraints clocks. It is reusable infrastructure for the Allwinner CCU descriptor files in this directory, translating CCF enable, parent, rate, and hardware readback requests into protected MMIO register updates.

## Important APIs, Types, And Functions
The file exposes a `const struct clk_ops` instance through the `SUNXI_CCU` namespace and uses `struct ccu_common` plus the class-specific descriptor from the matching header. Important routines include helpers to compute the best factors, `recalc_rate`, `determine_rate`, `set_rate`, gate wrappers, and any parent mux callbacks required by the class. It enforces optional maximum M/N ratio and minimum parent/M ratio constraints when selecting factors.

## Control Flow
Consumers enter through CCF callbacks. Read paths fetch the current register value, decode the configured bitfields, apply mux predividers or fixed postdividers, and return the effective rate. Rate-change paths choose the best representable factors, take the shared CCU spinlock, update only the relevant bitfields, release the lock, and wait for a PLL lock bit when the class carries one. Parent operations delegate to the mux helper where applicable.

## State And Persistence
The only persisted state is live hardware register state for the boot. The code does not write files or keep software caches; it mutates MMIO fields under the CCU lock and relies on CCF to serialize higher-level topology operations.

## Dependencies And Integration Points
It depends on Linux CCF helpers, `readl`/`writel`, spinlocks, `ccu_gate`, `ccu_mux`, and descriptor macros from adjacent sunxi-ng headers. Integration is indirect: SoC CCU drivers instantiate these structures and `devm_sunxi_ccu_probe()` registers them for device-tree clock consumers.

## Risks
Risk is concentrated in factor search and bitfield programming. Off-by-one offsets, zero-width fields, postdivider handling, mux predivider handling, or missing lock waits can silently produce bad peripheral, display, MMC, audio, or CPU rates. Changes must preserve register masks and `CLK_SET_RATE_PARENT` behavior.

## Test Signals
Useful signals are successful build of the sunxi-ng clock drivers, clean probe of affected SoC CCUs, sane `/sys/kernel/debug/clk/clk_summary` rates, and hardware validation of peripherals using each class: CPU/PLL scaling, display pixel clocks, MMC tuning, SPI/I2C/UART baud rates, audio sample clocks, and suspend/resume clock gating.
