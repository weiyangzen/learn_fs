# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/debug.h

## Purpose
`debug.h` defines ath11k debug mask bits, debug string mapping, logging prototypes, disabled-debug stubs, and the `ath11k_dbg()` macro used throughout the driver.

## Important APIs, Types, And Functions
`enum ath11k_debug_mask` assigns bitmasks for AHB, WMI, HTC, DP/HTT, MAC, boot, QMI, data, management, regulatory, testmode, HAL, PCI, DP TX/RX, CE, CFR, and CFR dumps. `ath11k_dbg_str()` maps each mask to a printable prefix. Prototypes cover info/error/warn and, when enabled, debug/dump functions. The `ath11k_dbg()` macro calls `__ath11k_dbg()` when either the mask is enabled or the debug tracepoint is active.

## Control Flow
Callers use `ath11k_dbg(ab, MASK, ...)`; the macro avoids debug formatting work unless logging or tracing needs it. For non-debug builds, inline stubs compile out debug printing and dump behavior while preserving call sites.

## State And Persistence
The header declares `extern unsigned int ath11k_debug_mask`, set through the module parameter in `core.c`. No persistent state is defined.

## Dependencies And Integration Points
It includes `trace.h` and `debugfs.h`, making it the bridge between driver logging, tracepoints, and debugfs-related declarations. Nearly every source file in ath11k can include it.

## Risks And Test Signals
Adding a debug mask requires updating `ath11k_dbg_str()` because there is intentionally no default case. Build tests catch missing enum handling. Runtime tests should verify that tracepoint-only debug still emits through `ath11k_dbg()` even when `debug_mask` is zero, and that disabled-debug builds do not leave unresolved symbols.
