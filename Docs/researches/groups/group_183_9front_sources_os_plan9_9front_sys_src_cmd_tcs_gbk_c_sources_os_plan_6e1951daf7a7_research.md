# Group Research: group_183_9front_sources_os_plan9_9front_sys_src_cmd_tcs_gbk_c_sources_os_plan_6e1951daf7a7

Scope checked against `Docs/research_subset_a.md`: `sources/os/plan9/9front` is included in subset A. All three listed files were read fully.

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.c -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.c

## Purpose

`gbk.c` is a generated/static mapping asset for the Plan 9/9front `tcs` character set converter. It exports `tabgbk[]`, a GBK-code-indexed table whose values are Unicode `Rune` code points or `-1` for unmapped/invalid GBK byte pairs.

## Structure

- Includes only `gbk.h`.
- Defines one global symbol: `long tabgbk[]`.
- Contains no functions, conditionals, macros, or executable logic.
- Full-file validation:
  - Lines: 4006
  - Bytes: 223095
  - SHA-256: `b2ac4e3446d8dbfdb344f9ba3c9d4822762ead7ca484b73b511279c7cca2eec5`
  - Table tokens: 32016
  - Mapped entries: 21791
  - `-1` holes: 10225
  - Lowest mapped value: `0x00a4`
  - Highest mapped value: `0xffe5`
  - CJK Unified Ideograph entries in `0x4e00..0x9fa5`: 20902
  - CJK Compatibility Ideograph entries in `0xf900..0xfaff`: 21
  - Values above BMP: 0
  - Duplicate mapped Unicode values: 0

## Indexing Contract

The table is intended to be addressed as:

`tabgbk[gbk_code - GBKMIN]`

where `GBKMIN` is `0x8140` and consumer code treats `GBKMAX` as an exclusive upper bound. The populated token count, 32016, matches the exclusive range `0x8140..0xfe4f`.

## Integration Points

- Declared by `gbk.h` as `extern long tabgbk[]`.
- Consumed by `conv_gbk.c`:
  - GBK input conversion looks up `tabgbk[c - GBKMIN]`.
  - GBK output conversion builds a reverse `Rune -> GBK code` table from `tabgbk`.
- Registered in `tcs.c` through the `"gbk"` converter entries that point to `gbk_in` and `gbk_out`.

## Important Notes

The table deliberately contains many `-1` sentinels for holes in the GBK byte-pair space. Any reverse-map builder must skip negative entries before indexing by the mapped Unicode value. The neighboring `conv_gbk.c` reverse-map loop should be reviewed with this in mind, because this table itself does not protect consumers from using `-1` as an array index.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.h

## Purpose

`gbk.h` provides the public constants and table declaration needed by the GBK converter implementation.

## Contents

- `#define GBKMIN 0x8140`
- `#define GBKMAX 0xFE50`
- `extern long tabgbk[];`

Full-file validation:
- Lines: 4
- Bytes: 67
- SHA-256: `ff5c23981d84f1ff743d4b8831078b9c1855a930353f18a22e8fd3f3582ec523`

## Integration Points

- Included by `gbk.c` to define/export the mapping table with the shared constants.
- Included by `conv_gbk.c` to decode GBK input and build GBK output mappings.

## Important Notes

`GBKMAX` is used by the converter as an exclusive bound (`c < GBKMAX`, `i < GBKMAX`), so the valid encoded GBK range is `0x8140` through `0xfe4f`, not including `0xfe50`.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/gbk.h -->

<!-- BEGIN FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/hdr.h -->
# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/hdr.h

## Purpose

`hdr.h` is the shared internal header for the `tcs` conversion pipeline. It defines global converter state, the converter descriptor type, input/output function signatures, buffering constants, and shared error-substitution constants.

## Contents

- External global flags/counters:
  - `squawk`, `clean`, `file`, `verbose`
  - `ninput`, `noutput`, `nrunes`, `nerrors`
- Converter flags:
  - `From = 1`
  - `Table = 2`
  - `Func = 4`
- `struct convert`, containing:
  - charset name
  - descriptive chatter text
  - flags
  - data pointer
  - function pointer
- Function pointer typedefs:
  - `Fnptr`
  - `Infn`
  - `Outfn`
- Shared conversion declarations:
  - `conv`
  - `outtable`
  - `fixsurrogate`
  - UTF and ISO-UTF input/output functions
  - `warn`
- Buffering:
  - `N = 10000`
  - external `Rune runes[N]`
  - external `char obuf[UTFmax*N]`
- Output dispatch macro:
  - `OUT(out, r, n)` dispatches either to `outtable` for table converters or to an output function for functional converters.
- Error constants:
  - `BADMAP = 0xFFFD`
  - `BYTEBADMAP = '?'`
  - `ESC = 033`

Full-file validation:
- Lines: 42
- Bytes: 1138
- SHA-256: `d17d303cf25059b54952205dfacc17a671ee929becedd7d02f45f9c5c2364ce4`

## Integration Points

`hdr.h` is included by converter implementation files such as `conv_gbk.c` and by the main `tcs.c` driver. It assumes Plan 9 base headers have already provided types/macros such as `Rune` and `UTFmax`.

## Important Notes

The `OUT` macro is central to the pipeline: input converters emit `Rune` batches without caring whether the destination charset is implemented as a simple table or a function. Since it is a macro with control flow and casts, changes to `struct convert` flags or function signatures would affect most converter modules.
<!-- END FILE RESEARCH: sources/os/plan9/9front/sys/src/cmd/tcs/hdr.h -->