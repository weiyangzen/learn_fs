# sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/settrace/settrace.cpp

## Purpose

`sources/distributed-fs/openafs/src/WINNT/afsrdr/tools/settrace/settrace.cpp` implements `SetTrace`, a command-line utility for configuring OpenAFS redirector debug tracing. The complete 202-line file was read.

## Important APIs, Types, and Functions

`usage` prints accepted switches. `main` parses `/l` for trace level, `/s` for subsystem, `/b` for trace buffer size in KB, and `/d` or `/f` for debug flags. It fills `AFSTraceConfigCB` and sends `IOCTL_AFS_CONFIGURE_DEBUG_TRACE`.

## Control Flow

The tool requires at least one option/value pair, opens `AFS_SYMLINK`, scans arguments, parses numeric values with `StrToIntExA`, and aborts on the first parse or option error. On success it copies parsed values into `AFSTraceConfigCB`, sends the configure IOCTL, prints success or `GetLastError()`, closes the device handle, and returns a small status code.

## State and Persistence Behavior

The program mutates driver trace configuration: subsystem, level, buffer length, and debug flags. Whether that state persists across driver restart is controlled by the redirector, not this tool.

## Dependencies and Integration Points

The file depends on `AFSUserDefines.h`, `AFSUserIoctl.h`, and `AFSUserStructs.h`. The kernel-side trace configuration handler is in `kernel/fs/AFSCommSupport.cpp`, with implementation in `kernel/fs/AFSLogSupport.cpp`. It pairs with `gettrace.cpp` for retrieval.

## Risks and Edge Cases

Each option increments `dwIndex` before reading the option value without checking bounds, so truncated command lines can read past `argv`. Unspecified fields remain at `-1` and are sent as unsigned `ULONG` values in `AFSTraceConfigCB`; this may be intentional as an unchanged sentinel, but it depends on driver semantics. The usage string advertises `/f`, while parsing also accepts `/d`. Open failure returns code `2`; parse failure returns code `4`; IOCTL failure returns code `3`, which is useful for scripts.

## Test Signals

Tests should set individual fields and all fields together, verify invalid and missing option values fail without changing driver state, confirm `GetTrace` observes the configured buffer behavior, and check that `-1` sentinel values are either ignored or deliberately applied by the driver as documented.
