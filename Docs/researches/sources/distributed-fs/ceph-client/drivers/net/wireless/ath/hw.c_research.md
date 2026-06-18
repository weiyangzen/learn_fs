<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/hw.c

Purpose: Provides shared ath hardware helpers for BSSID mask programming and cycle counter accounting.

Important APIs/types/functions: Exports `ath_hw_setbssidmask()`, `ath_hw_cycle_counters_update()`, and `ath_hw_get_listen_time()`. Uses `common->ops->read/write`, `AR_STA_ID*`, `AR_BSSMSK*`, `AR_MIBC`, and cycle counter registers from `reg.h`.

Control flow: `ath_hw_setbssidmask()` writes the current MAC and BSSID mask into PCU registers. `ath_hw_cycle_counters_update()` freezes MIB counters, reads cycle/busy/RX/TX counts, clears counters, unfreezes, and accumulates into ANI and survey counters. `ath_hw_get_listen_time()` computes listen time from ANI counters and clears that accumulator.

State and persistence: Updates hardware registers and in-memory `ath_common` counter accumulators. Counter state persists only in driver memory until consumed.

Dependencies and integration points: Shared by ath drivers that provide register ops and `ath_common`; results feed ANI and survey reporting.

Risks and test signals: Risks include missing `cc_lock` by callers, divide-by-zero if `clockrate` is invalid, and BSSID mask over-acceptance in multi-BSS modes. Test signals are survey statistics sanity, ANI behavior, multi-vif ACK filtering, and register read/write traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/hw.c -->
