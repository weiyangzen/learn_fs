# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/gcc_optimizations.h

## Purpose
`gcc_optimizations.h` centralizes branch prediction macros for native Hadoop code. It lets performance-sensitive C code annotate likely and unlikely branches when compiled by GCC-compatible compilers.

## Important APIs, types, and functions
The header defines `likely(x)` and `unlikely(x)`. Under `__GNUC__`, they expand to `__builtin_expect`; otherwise they evaluate to the expression unchanged.

## Control flow
There is no runtime control flow. The macros influence compiler branch layout and prediction hints at compile time.

## State and persistence
The header has no state. It only affects generated code in translation units that include it.

## Dependencies and integration points
It is included by checksum JNI and CRC implementation files where hot loops and validation branches benefit from predictable layout. `org_apache_hadoop.h` separately defines fallback branch macros for broader native code.

## Risks and test signals
Risks are macro name collisions, double evaluation if passed expressions with side effects, and portability to non-GCC compilers. Test signals are native builds with GCC/Clang and non-GNU toolchains plus warning-free compilation of CRC code.
