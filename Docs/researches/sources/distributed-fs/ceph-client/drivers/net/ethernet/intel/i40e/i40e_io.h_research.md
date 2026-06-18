# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_io.h

## Purpose
`i40e_io.h` is the i40e driver's small MMIO access wrapper. It provides register read/write macros used by HMC, LAN HMC, ethtool, diagnostics, and other hardware-control code.

## Important APIs, types, and functions
- `wr32(a, reg, value)` writes a 32-bit value to `a->hw_addr + reg` with `writel`.
- `rd32(a, reg)` reads a 32-bit register with `readl`.
- `rd64(a, reg)` reads a 64-bit register with `readq`.
- `i40e_flush(a)` reads `I40E_GLGEN_STAT` to flush posted writes.
- The header includes `linux/io-64-nonatomic-lo-hi.h` so 32-bit kernels get low-first `readq/writeq` support.

## Control flow and behavior
There is no runtime control flow beyond macro expansion. Callers pass an `i40e_hw`-like object with a mapped `hw_addr`; the macros perform direct MMIO at register offsets. `i40e_flush` is used after writes that must be visible to hardware before later operations.

## State and persistence
The macros mutate or observe hardware register state only. They do not keep software state and do not persist anything outside device registers.

## Dependencies and integration points
This header depends on Linux I/O accessors and register constants such as `I40E_GLGEN_STAT`. It is included by `i40e_hmc.h` and other driver files that perform direct register access.

## Risks and edge cases
- Callers must ensure `hw_addr` is valid and register offsets match the device generation.
- The macros do not include barriers beyond the semantics of `readl`/`writel`; callers use `i40e_flush` when posted-write ordering matters.
- `rd64` behavior on 32-bit platforms depends on the included non-atomic low-high implementation, so it is not suitable for registers requiring atomic 64-bit snapshots unless hardware documents that access pattern.

## Test signals
Build coverage confirms macro availability. Runtime indicators are absence of MMIO faults during probe, successful register dumps and HMC programming, and correct behavior of code paths that rely on `i40e_flush` after programming interrupt moderation, HMC, RSS, or Flow Director registers.
