# sources/distributed-fs/ceph-client/fs/pstore/internal.h

## Purpose
`internal.h` is the private interface between pstore core, filesystem presentation, and optional ftrace/pmsg frontends.

## Important APIs, types, and functions
It declares `kmsg_bytes`, `psinfo`, `pstore_set_kmsg_bytes`, record retrieval helpers, `pstore_mkfile`, `pstore_record_init`, filesystem init/exit hooks, and optional ftrace/pmsg registration functions with stub fallbacks.

## Control flow
Compile-time conditionals keep core call sites simple: when ftrace or pmsg is disabled, registration helpers become no-ops and ftrace log combining returns an empty result.

## State and persistence
The header owns no state directly, but exposes global pstore state and current backend pointer used by the compiled pstore objects.

## Dependencies and integration points
It depends on `linux/pstore.h`, time/types headers, and optional frontend configurations.

## Risks and test signals
Risks include signature drift between stubs and implementations, accidental use of `psinfo` before registration, and frontend-disabled behavior masking missing backend support. Test signals are compile coverage for all optional frontend combinations and runtime registration with pmsg/ftrace disabled.
