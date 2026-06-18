# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/primitives/asm/asm-const.h

## Purpose
`asm-const.h` is a minimal guard header for assembly constant compatibility in the primitives selftest copy of powerpc headers.

## Important APIs, Types, and Functions
It provides only the include guard and no active constants in this selftest snapshot.

## Control Flow and State
There is no runtime flow or state.

## Dependencies and Integration Points
It exists so headers imported from the kernel tree can include `<asm/asm-const.h>` without requiring the full kernel include environment.

## Risks and Test Signals
The risk is future imported code requiring missing constant helpers. The signal is continued successful build of primitive tests with this reduced header.
