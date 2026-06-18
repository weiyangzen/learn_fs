# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/mstring.h

## Purpose

`mstring.h` declares NetIDMgr utility APIs for Windows wide-character multi-strings and CSV conversion. A multi-string is a sequence of null-terminated strings terminated by an extra null, which this API uses for configuration values such as cell lists, recent realms, and status strings.

## Important APIs, types, and functions

The public constants are `KHM_PREFIX`, `KHM_CASE_SENSITIVE`, `KHM_MAXCCH_STRING`, and `KHM_MAXCB_STRING`. Core mutation APIs are `multi_string_init`, `multi_string_prepend`, `multi_string_append`, and `multi_string_delete`. Search and traversal are handled by `multi_string_find` and `multi_string_next`. Serialization APIs are `multi_string_to_csv` and `csv_to_multi_string`. Size and copy helpers include `multi_string_length_cb`, `multi_string_length_cch`, `multi_string_length_n`, `multi_string_copy_cb`, and `multi_string_copy_cch`.

## Control flow

This header only declares APIs, but the documented contract is two-pass friendly: callers pass a buffer size, and append/prepend/conversion APIs report `KHM_ERROR_TOO_LONG` plus the required byte count when the destination is too small or null. Search/delete behavior is controlled by exact versus prefix matching and case-sensitive versus default case-insensitive matching. Traversal starts at the first element and repeatedly calls `multi_string_next` until null.

## State and persistence behavior

The API operates on caller-owned buffers. It does not allocate persistent state in the header contract. Persistence enters through callers that store the multi-string in NetIDMgr configuration spaces or convert it to/from CSV resource strings.

## Dependencies and integration points

The header depends on `khdefs.h` for `KHMEXP`, `KHMAPI`, `khm_int32`, and `khm_size`. It is included by `utils.h` and by NetIDMgr configuration code. In this work item, `afsconfigdlg.c` uses `csv_to_multi_string` and `multi_string_next` to turn a localized service-status CSV resource into display strings.

## Risks and edge cases

The maximum size is fixed at 16,384 wide characters. Callers must distinguish byte counts from character counts and preserve the double-null terminator. Empty strings are invalid for append. Prefix matching can delete the first partial match, which is useful but risky for ambiguous cell or realm names. CSV conversion must preserve quoting and embedded quotes to avoid lossy configuration round trips.

## Test signals

Useful tests cover empty initialized strings, append/prepend buffer-too-small reporting, delete exact/prefix and case-sensitive/insensitive behavior, traversal across the final double-null, CSV quoting for commas and quotes, malformed CSV handling, and byte-versus-character copy limits.
