<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.h

## Purpose
`erasure_coder.h` defines native state structures and function prototypes for Hadoop's ISA-L-backed erasure coders.

## Important APIs, Types, and Functions
Constants `MMAX` and `KMAX` bound all-unit and data-unit sizes. `IsalCoder` stores verbosity and data/parity/all-unit counts. `IsalEncoder` adds `gftbls` and `encodeMatrix`. `IsalDecoder` adds matrices, erasure flags/indexes, decode indexes, erased count, and real input pointers. Prototypes expose init, encode, decode, clear, and decode-matrix generation routines.

## Control Flow
The header describes the object lifecycle used by JNI wrappers: initialize a coder, call encode/decode repeatedly, optionally enable verbose dumps, and free the wrapper allocation from the JNI destroy method.

## State and Persistence
All arrays are embedded in the coder structs and persist for the native object lifetime. Decoder per-call arrays are reused and cleared when erasure patterns change.

## Dependencies and Integration Points
It is included by the C erasure algorithm files and JNI bridge files. The first field of RS/XOR wrapper structs is intentionally compatible with `IsalCoder *` access through `nativeCoder`.

## Risks and Edge Cases
The static array sizes are hard limits; exceeding them corrupts memory if Java-side validation fails. The cast-based wrapper pattern requires `IsalCoder` or a struct containing it first in memory.

## Test Signals
Configuration-limit tests, ASAN runs, repeated encode/decode reuse, and Java native-coder pointer lifecycle tests validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/erasurecode/erasure_coder.h -->
