# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.c

Purpose: SoundWire bus driver for the RT722 SDCA codec. It creates a single 16-bit MBQ-capable SDCA regmap with per-register MBQ width selection, publishes SoundWire properties, handles SDCA interrupts, coordinates attach-time initialization, and implements PM for the RT722 ASoC component.

Important APIs and functions: `rt722_sdca_mbq_size()` is the core register classifier; it returns 1 for one-byte SDCA/HID/control registers, 2 for two-byte vendor/volume/gain registers, and 0 for inaccessible registers. `rt722_mbq_config` passes that classifier to `devm_regmap_init_sdw_mbq_cfg()` in `rt722_sdca_sdw_probe()`. `rt722_sdca_readable_register()` uses the same classifier, while `rt722_sdca_volatile_register()` marks live status, power-state, HID, and selected vendor registers. `rt722_sdca_read_prop()` configures source ports 2/6, sink ports 1/3, full data ports, paging, wake capability, lane control, and clock-stop timeout.

Control flow: `rt722_sdca_update_status()` clears `hw_init` on unattach, restores interrupt masks when a jack exists and the slave reattaches, and calls `rt722_sdca_io_init()` when needed. `rt722_sdca_interrupt_callback()` mirrors RT721: cancel pending jack work, snapshot SDCA interrupt status, clear SDCA cascade bits with retries, preserve pending status after canceled work, and schedule `jack_detect_work` unless suspended. System suspend sets `disable_irq` and masks SDCA interrupt bits under `disable_irq_lock`; resume restores masks when no detach occurred or waits up to 5 seconds for reinitialization after detach, then syncs regcache.

State and persistence: the bus driver owns no separate state beyond the `rt722_sdca_priv` allocated by the component. Regcache is marked cache-only on suspend and synced on resume. `hw_init`, `first_hw_init`, `disable_irq`, and `scp_sdca_stat*` are the key state variables shared with component jack/work handlers.

Dependencies and integration points: depends on SoundWire SDCA registers, regmap SDW MBQ configuration, runtime PM, delayed work coordination in `rt722-sdca.c`, and constants/defaults from `rt722-sdca.h` and `rt722-sdca-sdw.h`. Device ID is Realtek `0x025d`, part `0x722`, SDW v3 class tuple `(0x3,0x1,0)`.

Risks: correctness hinges on the large `rt722_sdca_mbq_size()` allowlist. A missing register can make valid component access fail; a wrong width can corrupt transactions. Interrupt clearing is retry-limited and races with suspend/workqueue scheduling. As with RT721, resume can replay stale cached state if initialization flags and cache dirtiness are not aligned.

Test signals: build and probe RT722 SDCA, verify MBQ widths using regmap debug or bus traces, test DP1/DP2/DP3/DP6 audio paths, trigger jack/button SDCA interrupts, suspend/resume with pending delayed work, detach/re-attach the slave, and confirm cached controls and interrupt masks are restored.
