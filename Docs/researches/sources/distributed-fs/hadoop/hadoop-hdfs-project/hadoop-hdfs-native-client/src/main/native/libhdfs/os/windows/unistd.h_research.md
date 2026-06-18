# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/os/windows/unistd.h

## Purpose
This compatibility header provides the minimal `unistd.h` functionality expected by libhdfs code on Windows.

## Important APIs, Control Flow, and State
It includes `<Windows.h>` and defines `sleep(seconds)` as `Sleep((seconds) * 1000)`. There is no runtime state beyond the delegated Windows sleep call.

## Dependencies and Integration Points
It is included by cross-platform C code that uses Unix `sleep` but must also build on Windows.

## Risks and Test Signals
The macro evaluates `seconds` once but performs multiplication in the argument expression, so large values can overflow the Windows millisecond type. Tests should compile Windows consumers and validate expected sleep duration for small values.
