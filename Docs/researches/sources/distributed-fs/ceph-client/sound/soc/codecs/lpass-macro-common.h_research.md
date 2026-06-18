# sources/distributed-fs/ceph-client/sound/soc/codecs/lpass-macro-common.h

## Purpose
`lpass-macro-common.h` declares shared LPASS macro flags, version enums, power-domain state, helper prototypes, and small inline helpers used by Qualcomm LPASS macro codec drivers.

## Important APIs, Types, And Constants
`LPASS_MACRO_FLAG_HAS_NPL_CLOCK` marks SoCs whose macro driver should request an NPL clock. `LPASS_MACRO_FLAG_RESET_SWR` records a SoundWire reset capability/requirement. `enum lpass_version` identifies broader LPASS platform versions, while `enum lpass_codec_version` identifies codec register-layout generations from unknown through v2.9. `struct lpass_macro` stores the `"macro"` and `"dcodec"` power-domain device pointers. The header declares the power-domain init/exit helpers and global codec-version get/set helpers implemented in `lpass-macro-common.c`.

Two inline helpers are important to users: `lpass_macro_pds_exit_action()` adapts the exit function to `devm_add_action_or_reset()`, and `lpass_macro_get_codec_version_string()` converts most known codec versions to readable strings.

## Control Flow
This header has no standalone runtime flow. Its inline cleanup action simply forwards a `void *` to `lpass_macro_pds_exit()`. The string conversion switch returns explicit strings for versions 1.0, 1.1, 1.2, 2.0, 2.1, 2.5, 2.6, 2.7, and 2.8, and falls back to `"NA"` for unknown or not-yet-listed values.

## State And Persistence
The header defines the shape of per-device power-domain state but does not allocate it. It also defines the enum values used by the global codec-version state in the C file. Since these enum values are ABI-like inside the driver family, changing order would affect every switch that persists or compares the numeric version.

## Dependencies And Integration Points
The header expects users to include kernel bit macros before or through surrounding includes; it uses `BIT()` in flag definitions. It is consumed by LPASS macro drivers such as `lpass-rx-macro.c` for flags, power-domain cleanup, and codec-version dispatch. Device match tables store the flag bits in `.data`, and probe code uses the version enum to select register maps.

## Risks And Notes
The string helper omits `LPASS_CODEC_VERSION_2_9`, returning `"NA"` even though the enum defines it. The header does not include `<linux/bitops.h>` itself, so standalone inclusion depends on prior includes for `BIT()`. The global codec-version model declared here is not per-device.

## Test Signals
Compile tests should include this header from each LPASS macro user. Functional tests should verify flag interpretation from OF match data, managed cleanup via `lpass_macro_pds_exit_action()`, and version-string output for every enum value, especially newer versions that may currently fall through to `"NA"`.
