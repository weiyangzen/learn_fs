<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/papr-sysparm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/papr-sysparm.h

## Purpose
This header defines the in-kernel PAPR system-parameter token type and RTAS buffer layout for `ibm,get-system-parameter` and `ibm,set-system-parameter`.

## Important APIs, Types, And Functions
It defines `papr_sysparm_t`, `mk_papr_sysparm()`, named parameters such as shared processor LPAR attributes, processor module info, cooperative memory overcommit attributes, TLB block invalidate attributes, LPAR name, and HVPIPE enable. `struct papr_sysparm_buf` contains a big-endian length and value buffer. It declares allocation/free plus `papr_sysparm_set()` and `papr_sysparm_get()`.

## Control Flow
Callers allocate a buffer, fill or receive the length-prefixed payload, and call RTAS-backed get/set helpers with a typed token.

## State And Persistence Behavior
The buffer is transient kernel memory. Actual parameter state is owned by firmware/hypervisor and may persist according to PAPR semantics.

## Dependencies And Integration Points
It depends on UAPI PAPR sysparm constants and RTAS pseries infrastructure. Consumers include pseries feature discovery and configuration code.

## Risks And Edge Cases
The RTAS work area layout differs from the user/kernel IO block. Length is big-endian and bounded by `PAPR_SYSPARM_MAX_OUTPUT`. Tokens must match PAPR-defined numbers.

## Test Signals
On pseries, query LPAR name and attributes, set supported writable parameters if available, test oversized buffers, and validate UAPI IO translation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/papr-sysparm.h -->
