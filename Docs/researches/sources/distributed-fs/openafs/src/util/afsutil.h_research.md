
# sources/distributed-fs/openafs/src/util/afsutil.h

Purpose: `afsutil.h` is the broad utility umbrella header for OpenAFS user-space utilities. It provides common includes, address sentinel constants, logging option types/macros, platform shims, base encoding typedefs, and pulls in `afsutil_prototypes.h`.

Important APIs and types: `AFS_IPINVALID` and `AFS_IPINVALIDIGNORE` identify invalid or absent address parsing results. `enum logDest`, `enum logRotateStyle`, and `struct logOptions` configure server logging to files or syslog. Logging APIs include `vFSLog()`, `FSLog()`, `OpenLog()`, `ReOpenLog()`, signal setup, log close, and getters. Macros `ViceLog`, `vViceLog`, and `ViceLogThenPanic` gate messages on `LogLevel`. `b32_string_t` and `lb64_string_t` define buffer sizes for encoders.

Control flow and integration: consumers include this header to get utility prototypes and platform differences in one place. Windows builds receive winsock initialization declarations and `setlinebuf` emulation; builds without POSIX regex get `re_comp`/`re_exec` declarations.

State and persistence: exposes `LogLevel` for logging macros and config structs for log destination, rotation, and filenames. Persistent effects are log files/syslog writes in implementation files outside this item.

Risks and test signals: as an umbrella header, include-order conflicts are possible. Macros evaluate logging arguments only when enabled, but panic macro depends on `osi_Panic`. Tests should compile representative Unix and Windows configurations, log rotation modes, and consumers of base string typedefs.
