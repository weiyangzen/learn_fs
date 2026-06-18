<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/link.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/link.c

Purpose: Provides ath9k runtime health monitoring, reset triggers, PLL workaround polling, PAPRD calibration, ANI/noise calibration, and survey counter maintenance. It is the link-maintenance layer that keeps the radio usable after TX/RX hangs, calibration failures, or changing channel/noise conditions.

Important APIs and functions: Public functions include `ath_hw_check_work()`, `ath_hw_check()`, `ath_hw_pll_work()`, `ath_paprd_calibrate()`, `ath_ani_calibrate()`, `ath_start_ani()`, `ath_stop_ani()`, `ath_check_ani()`, `ath_update_survey_nf()`, and `ath_update_survey_stats()`. Key helpers are `ath_tx_complete_check()`, `ath_hw_rx_inactive_check()`, `ath_hw_pll_rx_hang_check()`, `ath_paprd_send_frame()`, and `ath_paprd_activate()`.

Control flow: `hw_check_work` runs periodically and stops rescheduling if MAC alive checks, TX completion checks, or RX activity checks queue a reset. TX hang detection marks active AC queues as in progress on one pass and resets if they remain stuck on a later pass. RX inactivity expects at least roughly one interrupt per second over a four-second interval. PLL work runs only after beaconing/association and queues a reset after repeated bad PLL sums. ANI timer runs only when hardware is awake; it schedules long/short calibration and ANI monitor work, updates survey counters, queues resets on calibration failure, and reschedules itself at the shortest needed interval. PAPRD work sends training frames and activates per-chain predistortion tables once calibration succeeds.

State and persistence: Mutates queue `axq_tx_inprogress`, `rx_active_count`, `rx_active_check_time`, reset counters, `common->ani` timers and `caldone`, `PS_WAIT_FOR_ANI`, survey time/busy/RX/TX/noise fields, channel calibration flags such as `PAPRD_DONE`, and `ah->paprd_table_write_done`. All state is runtime-only but directly affects future reset, rate/noise, and power-save behavior.

Dependencies and integration points: Integrates with `ath9k_queue_reset()` in `main.c`, TX queue locks, `ath9k_hw_check_alive()`, AR9003 PLL/PAPRD helpers, mac80211 workqueue/timer APIs, power-save wake/restore, `ath9k_hw_calibrate()`, ANI monitor functions, survey reporting through `get_survey`, and common cycle counters.

Risks: False hang detection can cause disruptive resets under low traffic or delayed interrupts. The PLL hang counter is static, so behavior is shared across calls and assumes one active device context. ANI must not touch hardware while asleep except by setting wait flags. PAPRD reuses a single training skb across chains and relies on completion timing from TX completion. Survey math depends on clockrate and counter resets.

Test signals: Simulate TX queue hang, RX inactivity, MAC hang, PLL hang, and calibration failure reset types; verify ANI starts/stops with AP/STA/IBSS beacon state; inspect survey busy/noise updates; exercise PAPRD success, timeout, retrain, and activation paths; validate no work reschedules after a queued reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/link.c -->
