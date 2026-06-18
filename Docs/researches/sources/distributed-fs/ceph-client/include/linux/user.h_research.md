# sources/distributed-fs/ceph-client/include/linux/user.h

## Purpose
This compatibility header simply includes architecture-specific user register/core-dump definitions from `asm/user.h`.

## Important APIs, types, and functions
No Linux-generic APIs are defined here. The exported surface is whatever the target architecture provides through `asm/user.h`, typically user register and core-dump layout types.

## Control flow, state, and persistence
There is no control flow or state in this wrapper. It provides an include indirection for code that wants the generic `linux/user.h` path.

## Dependencies and integration points
It depends entirely on architecture headers and integrates with ptrace/core-dump and low-level user ABI code.

## Risks and test signals
Risks are architecture header divergence and accidental assumptions that this generic file defines common fields. Build coverage across architectures is the primary test signal.
