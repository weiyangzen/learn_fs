# sources/distributed-fs/ceph-client/arch/x86/kernel/tls.h

## Purpose
`tls.h` is the private declaration header for x86 TLS regset callbacks implemented in `tls.c`.

## Important APIs, Types, And Functions
It includes `<linux/regset.h>` and declares `regset_tls_active`, `regset_tls_get`, and `regset_tls_set` using generic user-regset callback typedefs.

## Control Flow
There is no runtime control flow; the header only supplies prototypes.

## State, Persistence, Dependencies, Integration
No state is owned. Its dependency is the regset API. Ptrace/user-regset registration code can include it to wire TLS descriptor access to the generic regset layer while keeping implementation private.

## Risks And Test Signals
Signature drift causes build failures. Build coverage with TLS regsets enabled is sufficient here; behavioral tests belong to `tls.c`.
