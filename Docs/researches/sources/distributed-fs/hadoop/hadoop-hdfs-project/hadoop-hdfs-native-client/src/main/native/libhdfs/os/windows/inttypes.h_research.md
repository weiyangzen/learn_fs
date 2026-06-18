# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/inttypes.h

## Purpose
This compatibility header supplies the small subset of `<inttypes.h>` needed by `libhdfs` on Windows.

## Important APIs, Control Flow, and State
It defines `PRId64` and `PRIu64` using MSVC-style `I64d` and `I64u`, and typedefs `uint64_t` as `unsigned __int64`. There is no runtime state or control flow.

## Dependencies and Integration Points
It is included where code expects integer format macros or `uint64_t` but the Windows toolchain lacks a suitable standard header.

## Risks and Test Signals
Modern Windows compilers often provide `<stdint.h>`/`<inttypes.h>`; duplicate typedefs or macro conflicts are possible if include ordering changes. Tests should compile under the supported MSVC versions and verify format strings used with these macros print correct 64-bit values.
