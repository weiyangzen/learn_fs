# sources/distributed-fs/eos/namespace/ns_quarkdb/QClPerformance.cc

Purpose: implements qclient performance metric collection for QuarkDB round-trip times.

Important APIs/types/functions: `QClPerfMonitor::SendPerfMarker` handles `"rtt_us"` markers, updating min, max, average, and per-minute peak map. `GetPerfMarkers` returns `rtt_min`, `rtt_max`, `rtt_avg`, `rtt_peak_1m`, `rtt_peak_2m`, and `rtt_peak_5m`.

Control flow: each RTT marker updates atomics and, under mutex, removes entries older than five minutes, updates the current minute peak, or inserts a new minute bucket. Metric collection scans recent buckets from newest to oldest to compute peak windows.

State and persistence: in-memory atomics and a mutex-protected minute-to-peak map. Metrics reset with process/group lifetime.

Dependencies and integration: implements `qclient::QPerfCallback` and is attached to qclient options by `QuarkNamespaceGroup::getQClient`.

Risks: average is an exponential-ish rolling average, not arithmetic mean. Initial `mMinRtt` is max integer until first marker. Atomic compare/update is not CAS-based, so concurrent updates may lose exact min/max races but remain approximate monitoring. `current_ts - 5` can underflow only at epoch-adjacent times.

Test signals: observable through namespace monitoring; no direct test in this subset.
