<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr.c

Purpose: OF helper support for DCR resources plus a shared lock for indirect DCR access.

Important APIs/types/functions: exported `dcr_resource_start()`, `dcr_resource_len()`, and `dcr_ind_lock`.

Control flow: helpers fetch the `dcr-reg` property, validate property presence, even cell count, and index range, then return the start or length cell for the requested resource.

State and persistence: no per-device state. `dcr_ind_lock` is a global spinlock used by indirect DCR access paths elsewhere.

Dependencies and integration points: depends on OF properties and `asm/dcr.h`. Drivers use these helpers to parse DCR resources from device tree nodes.

Risks: invalid `dcr-reg` properties return 0, which can be ambiguous if a real DCR resource starts at 0. Callers must handle missing/invalid resources carefully.

Test signals: drivers parsing DCR resources from representative device trees and serialized indirect access under concurrency validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/dcr.c -->
