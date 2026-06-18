# sources/distributed-fs/ceph-client/sound/soc/codecs/rt700-sdw.h

## Purpose
`rt700-sdw.h` supplies the RT700 logical regmap defaults used by the SoundWire transport driver. It is included by `rt700-sdw.c` and contains a large `static const struct reg_default rt700_reg_defaults[]` table for the cached codec regmap.

## Important APIs, Types, And Definitions
The only substantive object is `rt700_reg_defaults[]`. It lists default values for many logical RT700 register ranges: low codec state registers, SoundWire/HD-A helper windows around `0x2000`, amplifier and pin verb-like registers such as `0x7303`, `0x8383`, `0x7308`, `0x8388`, and private indexed registers encoded as 24-bit addresses such as `0x75201a`, `0x752045`, `0x752048`, `0x75204a`, and `0x75206b`.

## Control Flow Role
This header has no functions. At probe, `rt700-sdw.c` passes this table to the logical `rt700_regmap` configuration. Regmap uses the defaults to initialize the Maple cache, decide which cached values can be restored during resume, and provide baseline state before hardware initialization. The shared `rt700.c` initialization code writes many of the same registers explicitly after attach; this table is still important for suspend/resume and cached control behavior.

## State And Persistence Behavior
The default table defines the persistent software view of RT700 register state. Since the raw SoundWire regmap is uncached but the logical codec regmap is cached, these defaults determine what regcache believes until hardware writes occur and what values can be synchronized after cache-only periods. Indexed-private defaults are particularly important because resume sync in `rt700-sdw.c` includes the `0x752010..0x75206b` region.

## Dependencies And Integration Points
The header depends on `struct reg_default` from regmap, included indirectly by `rt700-sdw.c`. It is tightly coupled to `rt700_readable_register()`, `rt700_volatile_register()`, the custom read/write address translation, and resume sync ranges. It does not expose public symbols and is not a standalone interface.

## Risks
Incorrect defaults can cause regcache to skip needed writes or restore wrong codec values after suspend. Duplicate or inconsistent defaults can hide real hardware state transitions. Adding registers to `rt700.c` controls or initialization without adding readable/cache defaults and resume coverage may produce state loss across suspend. Because many values are magic hardware defaults, changes require datasheet or hardware validation.

## Test Signals
Build success confirms the table is visible to `rt700-sdw.c`. Runtime signals include stable ALSA controls after suspend/resume, no missing regcache sync for private registers, jack detection still enabled after resume, and no unexpected SoundWire transactions from stale cache defaults during initialization.
