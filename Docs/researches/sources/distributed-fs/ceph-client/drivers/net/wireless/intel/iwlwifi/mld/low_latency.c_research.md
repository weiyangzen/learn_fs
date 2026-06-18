# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.c

Purpose: Detects latency-sensitive VO/VI traffic and toggles firmware low-latency mode per MAC context. It also coordinates low-latency state with P2P client power settings and EMLSR retry behavior.

Important APIs/types/functions: `iwl_mld_low_latency_init()`, `iwl_mld_low_latency_free()`, `iwl_mld_low_latency_restart_cleanup()`, `iwl_mld_vif_update_low_latency()`, `iwl_mld_low_latency_update_counters()`, `iwl_mld_low_latency_stop()`, `iwl_mld_low_latency_restart()`, `iwl_mld_calc_low_latency()`, and `iwl_mld_send_low_latency_cmd()`.

Control flow: Data path calls `iwl_mld_low_latency_update_counters()` with packet header, STA, and RX/TX queue. QoS data packets with VO/VI TIDs increment per-queue/per-MAC counters and schedule work at 500 ms cadence. The worker sums counters by MAC, enables low latency immediately above threshold, disables only after the 10 second active period expires below threshold, then iterates active interfaces and updates VIF low-latency causes. State changes send `LOW_LATENCY_CMD`; P2P clients also update MAC power and retry EMLSR when enabling.

State/persistence: Allocates per-RX-queue counter arrays with spinlocks. Maintains per-MAC window start times, latest per-MAC low-latency result, global timestamp, delayed work, and a stopped flag. VIF low-latency causes are bitfields in `iwl_mld_vif`.

Dependencies/integration: Depends on mac80211 QoS headers/TIDs, MLD STA/VIF mappings, firmware MAC configuration commands, power management, MLO/EMLSR helpers, and wiphy delayed work.

Risks: Counter updates run in data-path context and must use spinlocks. `sta` and VIF mappings must be valid; invalid firmware IDs or queue IDs are dropped with warnings. Work is suppressed during hardware restart and stopped during driver stop. Thresholds are constants, so behavior may be sensitive to traffic bursts and queue count.

Test signals: Tests should simulate VO/VI and non-VO/VI packets, threshold crossing, delayed disable after active window expiry, restart cleanup counter reset, stop/restart behavior, command failure rollback of VIF cause bits, and P2P client power/EMLSR side effects.
