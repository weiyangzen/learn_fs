# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/wfx.h

Purpose: Central private data header for the Silicon Labs WFX mac80211 driver. It defines device-wide and virtual-interface state shared across bus, HIF, TX/RX, scan, power, and queue code.

Important APIs and types: `struct wfx_dev` holds platform data, device and mac80211 handles, two VIF slots, hardware bus callbacks, firmware startup data, HIF command state, bottom-half workqueue, TX pending queues, packet/key maps, scan/config mutexes, and RX/TX statistics. `struct wfx_vif` stores per-interface channel/id, link map, power-save/join state, beacon-loss work, four TX queues, TX policy cache, TIM update work, scan work, and remain-on-channel state. Inline helpers include `wvif_to_vif`, `wdev_to_wvif`, `wvif_iterate`, `wvif_count`, `memreverse`, and `memzcmp`.

Control flow: The header provides safe VIF lookup and iteration. `wdev_to_wvif` validates the VIF index, uses `array_index_nospec` to avoid speculative out-of-bounds access, and maps mac80211 `drv_priv` into driver-private VIF data. `wvif_iterate` walks the two VIF slots from either the start or after a current VIF.

State and persistence: State is in memory only and bound to mac80211 device lifetime. Important synchronization primitives are mutexes, completions, wait queues, atomics, work items, and delayed work.

Dependencies and integration: Includes mac80211, Linux workqueue/mutex/completion APIs, and WFX local headers for bottom-half, TX, queue, and HIF command handling. Other WFX files include this header to share the common object model.

Risks: Many fields are concurrency-sensitive and rely on external locking conventions not documented here. The driver supports exactly two VIF slots, so code using VIF IDs must respect that limit. `memzcmp` returns `memcmp(buf, buf + 1, size - 1)` after checking the first byte, which is compact but non-obvious.

Test signals: Compile coverage should catch struct/member drift. Runtime testing should exercise two-VIF lookup/iteration, VIF add/remove, scan and TX paths, and invalid VIF ID debug paths.
