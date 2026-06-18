# sources/compression/xz/src/liblzma/api/lzma/lzma12.h

Purpose: declares LZMA1, extended LZMA1, and LZMA2 filter IDs, match-finder/mode enums, the shared LZMA options structure, and preset helper.

Important APIs/types/functions: defines `LZMA_FILTER_LZMA1`, `LZMA_FILTER_LZMA1EXT`, `LZMA_FILTER_LZMA2`; enums `lzma_match_finder` (`HC3`, `HC4`, `BT2`, `BT3`, `BT4`) and `lzma_mode` (`FAST`, `NORMAL`); support queries `lzma_mf_is_supported`, `lzma_mode_is_supported`; struct `lzma_options_lzma` with dictionary, preset dictionary, literal/position bits, mode, nice length, match finder, depth, extended LZMA1 flags/size, and reserved ABI fields; macro `lzma_set_ext_size`; function `lzma_lzma_preset`.

Control flow: callers either fill options manually or call `lzma_lzma_preset()` for preset levels/flags, then attach options to `lzma_filter` chains. Raw LZMA1EXT uses the extended size/end-marker fields to model formats such as 7z.

State and persistence: options are caller-owned configuration. Encoder/decoder runtime state lives in filter implementations after initialization.

Dependencies/integration: consumed by `container.h` high-level encoders, `filter.h` raw APIs, xz option parsing, and memory-usage estimators. LZMA2 is the normal `.xz` terminal compression filter.

Risks: many options have cross-field constraints (`lc + lp <= 4`, dictionary limits, match finder support, depth DoS risk). Preset success does not guarantee every feature is enabled in a reduced build. Preset dictionaries are not supported by normal container decoders.

Test signals: filter flag/string tests, CLI option parsing, preset/memory usage tests, MicroLZMA tests, and stream round trips with LZMA1/LZMA2.
