# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-trap.c

Purpose: checks that thread endianness is not inadvertently flipped on traps taken in TM when FP/VEC state is unavailable or after context-switch pressure.

Important APIs/types/functions: `trap_signal_handler()` manipulates MSR.LE and NIP based on trap event and machine endianness; `ping()` executes endian-sensitive instruction sequence in TM; `pong()` induces context switches; `tm_trap_test()` binds both threads to one CPU.

Control flow: after HTM skips, the test installs SIGTRAP and SIGUSR1 handlers, creates two CPU-affined threads, waits for context-switch pressure, and executes a sequence whose native/opposite-endian interpretations route to success or failure labels. Handler logic adapts for LE and BE machines.

State and persistence behavior: globals `trap_event`, `le`, `success`, thread IDs, and exit flag coordinate the two threads and signal handler.

Dependencies and integration points: requires real HTM, pthread affinity, raw instruction encodings, and powerpc signal context MSR/NIP access.

Risks and test signals: very timing and architecture sensitive. Success prints that endianness did not flip; failure returns nonzero after routing to failure label.
