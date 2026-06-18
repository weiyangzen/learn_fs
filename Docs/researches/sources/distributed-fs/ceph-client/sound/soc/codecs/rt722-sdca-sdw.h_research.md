# sources/distributed-fs/ceph-client/sound/soc/codecs/rt722-sdca-sdw.h

Purpose: RT722 SDCA regmap-default header. It supplies `rt722_sdca_reg_defaults[]` for the single MBQ-configured SDCA regmap created by `rt722-sdca-sdw.c`.

Important data: the defaults include low SDCA/vendor registers (`0x2f*`, `0x200*`, `0x581*`, `0x610*`) plus constructed SDCA control addresses for jack codec, mic array, HID-adjacent function controls, amp controls, sample-frequency indices, request-power states, mute defaults, volume defaults, and function-unit channel gains. Defaults put major paths in muted or PS3-like safe states and set 48 kHz-style sample-frequency indices (`0x09`) initially.

Control flow and integration: the header has no functions. `rt722-sdca-sdw.c` plugs this array into `rt722_sdca_regmap` using `REGCACHE_MAPLE`; the same source determines whether each register is one or two bytes with `rt722_sdca_mbq_size()`. The component source later updates these cached values during preset, DAPM, mixer, and PCM operations.

State and persistence: static defaults seed software regcache before attach and after allocation. Runtime persistence comes from regcache mutations, dirty marking, and resume sync. Since RT722 uses one width-aware regmap rather than separate normal/MBQ regmaps, the defaults must match the width classifier exactly.

Dependencies: includes Linux regmap and SoundWire registers and relies on RT722 SDCA constants from `rt722-sdca.h` in the including source. It is coupled to both the MBQ classifier and the component register writes.

Risks: a default address absent from the MBQ-size allowlist will not be readable/writable through the configured regmap as expected. Width mismatches are particularly risky because a 1-byte default for a 2-byte control, or vice versa, can produce incorrect cache sync. Defaults may become stale relative to the guarded function-initialization presets in `rt722-sdca.c`.

Test signals: run regcache sync tests across runtime/system suspend, compare default and live values for mute/power/sample-rate controls, validate that every default address has a nonzero MBQ size classifier, and exercise audio/jack paths after detach/re-attach.
