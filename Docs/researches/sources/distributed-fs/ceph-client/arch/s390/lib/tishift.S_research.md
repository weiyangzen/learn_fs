# sources/distributed-fs/ceph-client/arch/s390/lib/tishift.S

## Purpose
Provides s390 assembly implementations of compiler helper functions for shifting 128-bit integers.

## Important APIs, Types, And Functions
Exports `__ashlti3` for arithmetic/logical left shift, `__ashrti3` for arithmetic right shift, and `__lshrti3` for logical right shift. The file lives in `.noinstr.text` and emits a nospec return thunk for `%r14`.

## Control Flow And State
Each helper loads a 128-bit value from the input pointer into `%r0/%r1`, handles zero shift as a direct store, branches between shifts below 64 bits and shifts of 64 or more, combines high/low halves with `ogr` where needed, sign-extends for arithmetic right shifts, stores the result to the output pointer, and returns.

## Dependencies And Integration
Depends on s390 linkage/export/nospec macros and compiler runtime expectations for `__int128` shift helpers. Used when generated kernel code needs 128-bit shifts not inlined by the compiler.

## Risks And Test Signals
Risks include ABI register/pointer convention mistakes, boundary errors at shift counts 0/63/64/127, wrong sign extension, and noinstr constraints. Signals include compiler-generated 128-bit arithmetic tests, boot with configs using `__uint128_t`, and objdump/assembler validation.
