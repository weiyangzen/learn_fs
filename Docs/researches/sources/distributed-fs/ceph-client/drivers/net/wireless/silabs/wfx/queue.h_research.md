# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/queue.h

Purpose: Declares WFx TX queue structures and queue/pending/flush helper APIs.

Important APIs and types: `struct wfx_queue` contains normal, CAB, and offchannel SKB queues plus pending-frame count and scheduling priority. Exports TX lock/flush helpers, queue init/check/has_cab/put/get/drop helpers, pending lookup/drop/delay/dump helpers, and queue-empty check.

Control flow and integration: Data TX, station AP TIM handling, BH TX, and flush/remove paths use these APIs to move SKBs from mac80211 to firmware and back to status reporting.

State and persistence: Per-vif queue state persists for the lifetime of an interface; pending state persists until firmware confirmation or frozen-chip cleanup.

Dependencies: Depends on SKB queues, atomics, and HIF message forward declarations from adjacent headers.

Risks and test signals: Tests should verify queue lifecycle on add/remove interface, pending count accuracy, CAB detection, and frozen-device cleanup contracts.

Test signals: Source read size: 45 lines, 1488 bytes.
