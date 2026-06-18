# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/dynack.c

Purpose: Implements dynamic ACK timeout estimation for ath9k, using TX status timestamps and received ACK timestamps to tune ACK/CTS timeout and slot time for long-distance or reduced-rate channels.

Important APIs/functions: Exported APIs are `ath_dynack_sample_tx_ts()`, `ath_dynack_sample_ack_ts()`, `ath_dynack_node_init()`, `ath_dynack_node_deinit()`, and `ath_dynack_reset()`. `ath_dynack_init()` initializes the feature but is not exported in this file. Internal helpers compute max timeout by channel width, EWMA station timeout, SIFS by PHY/rate mode, BSSID-mask ACK filtering, hardware timeout programming, and aggregate max timeout across nodes.

Control flow: TX completion sampling ignores disabled dynack and NO_ACK frames. XRETRY on association/auth frames is treated as late ACK: hardware timeout is raised to the channel max, station timeout is invalidated, and recomputation is delayed. Otherwise TX timestamp, duration, destination/source, and adjusted legacy duration are pushed into a ring buffer. ACK RX sampling filters by BSSID mask and pushes timestamps into a second ring. `ath_dynack_compute_to()` pairs TX and ACK ring heads, computes ACK propagation time after TX duration, bounds it below channel max, updates the matching station's EWMA `ackto`, and periodically recomputes the hardware timeout as the maximum station timeout. Reset clears rings, sets all nodes to max timeout, and programs hardware.

State/persistence: State lives in `ah->dynack`: enabled flag, qlock, node list, station TX ring, ACK ring, current `ackto`, and delayed recompute jiffies `lto`. Each `ath_node` stores `ackto` and a list node. Hardware state is ACK timeout, CTS timeout, and slottime registers.

Dependencies/integration: Depends on mac80211 station lookup, ath TX/RX status timestamps, channel width helpers, rate flags, hardware timeout setters, BSSID mask state, and `NL80211_FEATURE_ACKTO_ESTIMATION`.

Risks: Ring pairing is heuristic and can mismatch ACKs under heavy traffic or multiple peers. List updates require `qlock`; station lifetime must pair node init/deinit. Late-ACK behavior can hold maximum timeout for `LATEACK_DELAY`. Slottime derives from timeout with `(to - 3) / 2`, so invalid small values would be unsafe, though computed bounds avoid that.

Test signals: Enable/disable dynack, station add/remove, long-distance ACK timeout convergence, late ACK on auth/assoc, HT40/normal/half/quarter max timeout selection, BSSID mask filtering, ring wrap behavior, and hardware ACK/CTS/slottime programming after reset and recompute.
