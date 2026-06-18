# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/low_latency.h

Purpose: Defines low-latency detection state, cause bits, packet counters, and public low-latency lifecycle/update APIs.

Important APIs/types/functions: `struct iwl_mld_low_latency_packets_counters`, `enum iwl_mld_low_latency_cause`, `struct iwl_mld_low_latency`, and prototypes for init/free/restart cleanup, VIF update, counter update, stop, and restart.

Control flow: The header defines the data contract used by data-path calls and worker code. Cause bits allow multiple independent sources, such as traffic, debugfs, and VIF type, to request low latency without clearing each other accidentally.

State/persistence: Packet counters are cacheline-aligned and protected by spinlocks. The main state stores delayed work, timestamps, per-MAC windows/results, allocated counters, and stop status.

Dependencies/integration: Relies on `NUM_MAC_INDEX_DRIVER`, `struct iwl_mld`, mac80211 headers, and VIF-level low latency cause storage.

Risks: Cause bits must remain unique bit values. The per-MAC arrays must stay in sync with firmware MAC ID array sizes. Counter allocation size depends on transport RX queue count.

Test signals: Compile-time and runtime tests should confirm array bounds with firmware ID validation, independent cause-bit set/clear behavior, and safe counter updates across all RX queues.
