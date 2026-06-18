# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.h

## Purpose
`debug.h` defines the ath6kl debug and logging interface. It declares debug mask bits, exported logging functions, target stats read API, workaround identifiers, debug-only hooks, and no-op stubs when `CONFIG_ATH6KL_DEBUG` is disabled.

## Important APIs, types, and functions
`enum ATH6K_DEBUG_MASK` assigns bit flags for credit, WLAN TX/RX, BMI, HTC, HIF, IRQ, WMI, generic trace, scatter, cfg80211, raw bytes, aggregation, SDIO, boot, suspend, USB, and recovery logs, plus `ATH6KL_DBG_ANY`. The always-available logging functions are `ath6kl_printk()`, `ath6kl_info()`, `ath6kl_err()`, and `ath6kl_warn()`. Debug builds add `ath6kl_dbg()`, `ath6kl_dbg_dump()`, register dump hooks, credit dump hooks, firmware log event ingestion, workaround accounting, roam-table event ingestion, debug state setters, init, debugfs init, and cleanup.

## Control flow and integration
Callers can use the same debug APIs regardless of build configuration. In debug builds, calls route to `debug.c` and tracepoints; in non-debug builds, most debug hooks compile away, while info/error/warn logging remains available. This allows HTC/HIF/core code to keep instrumentation calls without surrounding each call with `#ifdef`.

## State and persistence behavior
This header declares `extern unsigned int debug_mask`, which controls runtime debug verbosity in debug builds. It does not own storage itself. The no-op stubs avoid persistent debug state when `CONFIG_ATH6KL_DEBUG` is off.

## Dependencies and integration points
`debug.h` includes `hif.h` and `trace.h`, so users get access to HIF-visible register structures and tracepoint declarations. This contributes to ath6kl's tight local header coupling but keeps instrumentation declarations centralized.

## Risks and test signals
Risks are mostly interface-level: adding a debug hook must keep stub and real signatures identical, and debug mask bit reuse can break user expectations. Build tests should cover both `CONFIG_ATH6KL_DEBUG=y` and disabled configurations. Runtime tests should verify `debug_mask`-gated logs and tracepoints still work in debug builds.
