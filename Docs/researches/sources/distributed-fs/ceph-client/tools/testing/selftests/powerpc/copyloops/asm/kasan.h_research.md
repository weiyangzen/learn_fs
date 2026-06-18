# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/kasan.h

## Purpose
Intentionally empty compatibility shim used so copied kernel copyloop assembly can include kernel-style headers without pulling in the full kernel tree.

## Important APIs, Types, and Functions
No macros, types, or functions are defined in this snapshot.

## Control Flow
There is no control flow; the file only satisfies include-path resolution.

## State and Persistence
No state is held or persisted.

## Dependencies and Integration Points
Included by copied assembly files that expect `<asm/...>` headers. Its integration role is to make absence explicit and keep the selftest build minimal.

## Risks and Test Signals
Risk is silent build breakage if future copied assembly starts relying on real definitions from this header. The current test signal is successful assembly with an empty shim.
