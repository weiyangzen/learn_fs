# sources/distributed-fs/openafs/src/util/volparse.c

Purpose: Provides partition-name parsing/formatting and robust integer parsing helpers for OpenAFS command-line and volume utilities.

Important APIs: `volutil_GetPartitionID()` maps numeric ids, `a`, `aa`, `vicepa`, and `/vicepa` forms to partition indexes. `volutil_PartitionName2_r()`, `volutil_PartitionName_r()`, and non-reentrant `volutil_PartitionName()` convert ids back to `/vicep*`. Numeric parsers include `util_GetInt32()`, `util_GetUInt32()`, `util_GetHumanInt32()`, `util_GetInt64()`, and `util_GetUInt64()`.

Control flow and state: Partition parsing accepts 0..254 and one/two-letter suffixes. Number parsing skips leading spaces/tabs, supports decimal, octal, and hex prefixes, checks digits for the inferred base, and uses rearranged overflow tests before multiply/add. Human int parsing uses `strtol()` plus `K`, `M`, `G`, or `T` binary multipliers.

Dependencies and integration: Includes `afsutil.h`; used by bos/vol/vos-style command parsing and table sorting (`tabular_output.c` uses `util_GetInt64()`).

Risks and test signals: Unsigned parsers do not accept a leading plus or minus. Empty numeric strings can parse as zero because no digit-count check occurs after prefix handling. `volutil_PartitionName()` uses static storage. Tests should cover partition boundaries (`z`, `aa`, max 254), invalid suffixes, numeric overflows, bases, and human suffixes.
