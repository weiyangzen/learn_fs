# sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/tests/enumresources.c

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/npdll/tests/enumresources.c` is a standalone WNet enumeration smoke test adapted from MSDN sample code. It exercises all installed Windows network providers, including OpenAFS when registered, by calling `WNetOpenEnum`, `WNetEnumResource`, and `WNetCloseEnum` for several scopes. The complete 322-line file was read.

## Important APIs, Types, and Functions

`main` enumerates `RESOURCE_CONNECTED`, `RESOURCE_CONTEXT`, `RESOURCE_GLOBALNET`, and `RESOURCE_REMEMBERED` for `RESOURCETYPE_DISK`. `EnumerateFunc` performs recursive enumeration with a 16 KiB `GlobalAlloc` buffer and `cEntries = -1`. `DisplayStruct` decodes `NETRESOURCE` scope, type, display type, usage flags, local name, remote name, comment, and provider. A commented `NetErrorHandler` shows extended-error handling but is not compiled.

## Control Flow

The program prints a heading for each scope, calls `EnumerateFunc`, and exits with `1` on the first failed scope. `EnumerateFunc` opens an enumeration handle, repeatedly zeroes the buffer and calls `WNetEnumResource` until `ERROR_NO_MORE_ITEMS`, displays each returned entry, and recursively descends into container entries only for `RESOURCE_GLOBALNET`.

## State and Persistence Behavior

The tool keeps only process-local heap state and does not persist data. Its observable behavior depends on system network-provider registration, current user connections, remembered mappings, and provider-specific enumeration implementations.

## Dependencies and Integration Points

The file links against `mpr.lib` and includes `windows.h`, `stdio.h`, and `winnetwk.h`. For OpenAFS, it indirectly drives `NPOpenEnum`, `NPEnumResource`, and `NPCloseEnum` in `AFS_Npdll.c` through the Windows Multiple Provider Router.

## Risks and Edge Cases

The code assumes a 16 KiB buffer remains adequate; providers can return `ERROR_MORE_DATA`, but this sample prints an error and breaks instead of resizing. Recursive global enumeration can be expensive or noisy on systems with many network providers. It uses `%S` for nullable string fields without null checks; OpenAFS sometimes returns null local/comment fields, so output behavior depends on the C runtime's handling of null wide-string pointers.

## Test Signals

Successful output over connected, context, and global scopes is a useful manual signal that OpenAFS provider enumeration works and returns well-formed `NETRESOURCE` strings. Useful variations include running with no AFS redirector, with one drive-letter connection, with a deviceless UNC connection, and with a deliberately small modified buffer to verify provider `WN_MORE_DATA` behavior.
