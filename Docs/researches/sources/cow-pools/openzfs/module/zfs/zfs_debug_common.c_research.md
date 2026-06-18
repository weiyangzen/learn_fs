# File Research: sources/cow-pools/openzfs/module/zfs/zfs_debug_common.c

## Summary
Provides common debug-message helpers, specifically dumping an nvlist tree through `zfs_dbgmsg()`.

## Main Responsibilities
- Splits multi-line strings into individual debug messages.
- Formats an nvlist with indentation.
- Emits each formatted line through the platform debug-message backend.
- Exports the nvlist debug helper in kernel builds.

## Key APIs
- `__zfs_dbgmsg_nvlist()`

## Important Behavior
`__zfs_dbgmsg_nvlist()` first computes the formatted nvlist length with `nvlist_snprintf(NULL, 0, ...)`, allocates a buffer, formats the nvlist, then repeatedly replaces newline characters with NUL terminators and logs one line at a time.

## Risks
The line splitter modifies the formatted buffer in place. Very large nvlists allocate a contiguous buffer sized to the full formatted representation.
