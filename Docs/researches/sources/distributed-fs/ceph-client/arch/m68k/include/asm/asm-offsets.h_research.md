<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-offsets.h

## Purpose
This shim header includes the generated m68k `asm-offsets.h` file. It gives assembly and C sources a stable include path for offsets computed during the build.

## Important APIs, Types, And Functions
- `#include <generated/asm-offsets.h>` is the only interface.

## Control Flow
There is no runtime control flow. The compiler/preprocessor substitutes generated constants at build time.

## State And Persistence Behavior
The header stores no state. The generated include contains build-derived offsets for structures used by low-level assembly.

## Dependencies And Integration Points
It depends on the architecture build generating `generated/asm-offsets.h` before sources that include this file are compiled.

## Risks And Edge Cases
If generated offsets are stale or missing, low-level entry and context-switch code can assemble with wrong or absent constants.

## Test Signals
A clean m68k build from no generated headers validates generation ordering and offset availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/asm-offsets.h -->
