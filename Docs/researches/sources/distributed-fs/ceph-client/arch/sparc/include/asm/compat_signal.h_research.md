<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat_signal.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat_signal.h

## Purpose
This header defines SPARC compat signal handling glue.

## Important APIs, Types, and Functions
It provides compat signal stack/context type declarations and helpers needed by SPARC64 when delivering signals to 32-bit tasks.

## Control Flow
Signal setup and return paths use these definitions to build and restore the 32-bit signal frame.

## State and Persistence Behavior
State is in the user signal frame and task registers; the header has none.

## Dependencies and Integration Points
It integrates with `compat.h`, signal delivery, ptrace, and ELF personality handling.

## Risks
Frame layout drift breaks signal return and can corrupt user registers.

## Test Signals
Run 32-bit signal tests on SPARC64, including alternate stacks, SA_SIGINFO, nested signals, and ptrace signal injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/compat_signal.h -->
