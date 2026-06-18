# sources/distributed-fs/ceph-client/lib/crc/sparc/crc32c_asm.S

## Purpose
This assembly file implements the SPARC64 CRC32C opcode loop used by `crc32c_arch()`.

## Important APIs, Types, and Functions
It defines `ENTRY(crc32c_sparc64)`, with arguments `%o0=crc32p`, `%o1=data_ptr`, and `%o2=len`. It uses `VISEntryHalf`/`VISExitHalf` and the `CRC32C` opcode macro.

## Control Flow
The function loads the current CRC into a floating/vector register, loops over 8-byte chunks with `ldd`, applies the CRC32C opcode, decrements length by 8, advances the pointer, stores the final CRC back, and returns.

## State and Persistence
The only state is the inout CRC word pointed to by `%o0` and transient VIS/FPU state managed by entry/exit macros.

## Dependencies and Integration Points
It depends on SPARC opcode, VIS, ASI, and linkage headers. The C header ensures it is called only on aligned 8-byte bodies after feature detection.

## Risks and Test Signals
Risks include VIS state handling, length not being a multiple of 8 if the caller changes, and endian/ASI load-store semantics. CRC32C KUnit and stress tests in interrupt/task contexts are useful signals.
