# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.h

## Purpose
Declares ath12k debug masks, logging APIs, global module parameters, and compile-time debug stubs/macros.

## Important APIs, Types, And Functions
Defines `enum ath12k_debug_mask` with masks for AHB, WMI, HTC, DP/HTT, MAC, boot, QMI, data, management, regulatory, testmode, HAL, PCI, DP TX/RX, WOW, CE, and any. Declares `ath12k_info()`, `ath12k_err()`, `__ath12k_warn()`, optional `__ath12k_dbg()`, and optional `ath12k_dbg_dump()`. Provides `ath12k_warn()`, `ath12k_hw_warn()`, `ath12k_dbg()`, and `ath12k_generic_dbg()` macros.

## Control Flow
`ath12k_dbg()` evaluates the mask once and only calls the debug function when the global mask enables it. Without `CONFIG_ATH12K_DEBUG`, debug functions compile to no-ops while info/error/warn remain available.

## State And Persistence
Declares external `ath12k_debug_mask` and `ath12k_ftm_mode`, both defined as module parameters in `core.c`.

## Dependencies And Integration Points
Includes `trace.h`, though trace emission is currently only marked as TODO in `debug.c`. Used across the driver as the common logging contract.

## Risks
`ath12k_warn(ab, ...)` assumes `ab` is non-null and has a valid device. Debug-only behavior can hide code path format warnings if not built with debug enabled, though printf annotations help.

## Test Signals
Compile both debug and non-debug configs. Validate each debug mask via module parameter and ensure generic debug with a null base prints with the fallback prefix.
