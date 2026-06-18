## sources/distributed-fs/ceph-client/sound/hda/core/regmap.c

Purpose: maps HD-audio codec verbs into a regmap-backed pseudo-register interface with caching, power-management retries, and special handling for asymmetric verb encodings.

Important APIs, types, and functions: `snd_hdac_regmap_init()`, `snd_hdac_regmap_exit()`, `snd_hdac_regmap_add_vendor_verb()`, `snd_hdac_regmap_write_raw()`, `snd_hdac_regmap_read_raw()`, `snd_hdac_regmap_read_raw_uncached()`, `snd_hdac_regmap_update_raw()`, `snd_hdac_regmap_update_raw_once()`, `snd_hdac_regmap_sync()`, `hda_reg_read()`, `hda_reg_write()`, and `hda_regmap_cfg`.

Control flow: regmap callbacks classify readable/writeable/volatile pseudo registers, acquire codec power when needed, translate GET-style pseudo registers into SET verbs for writes, and execute HD-audio verbs. Raw helpers serialize on `codec->regmap_lock`, optionally use regcache, and retry `-EAGAIN` by power-cycling through PM.

State and persistence: per-codec state includes `codec->regmap`, `vendor_verbs`, regcache contents, `cache_coef`, `caps_overwriting`, and `lazy_cache`. Cached values survive until regmap exit and are synced on resume.

Dependencies and integration points: depends on Linux regmap, HD-audio verb execution, codec PM helpers, and `snd_array` for vendor verbs. Used by codec parsers and controls to avoid repeated direct verb handling.

Risks: pseudo-register encoding is subtle, especially stereo amp and coefficient access. Cache policy must mark volatile hardware state correctly; stale cache can misprogram resume. Lazy-cache behavior can hide write failures while powered down. `caps_overwriting` intentionally suppresses writes.

Test signals: test amp left/right writes, coefficient cache, vendor verbs, power-state reads, pin-sense volatile reads, suspend/resume regcache sync, and no-regmap fallback paths; enable dynamic debug for failed verb execution.
