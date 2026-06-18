<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmapi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmapi.h

## Purpose
Provides common ATM UAPI compatibility helpers for architecture-specific alignment and opaque kernel pointer representation.

## Important APIs, Types, And Functions
`__ATM_API_ALIGN` expands to 8-byte alignment on sparc/ia64 and empty elsewhere. `atm_kptr_t` is an opaque 8-byte aligned struct used to pass kernel pointer tokens without exposing pointer type details.

## Control Flow
Other ATM headers use these definitions in structs exchanged with userspace. Userspace treats `atm_kptr_t` as an opaque token and passes it back unchanged.

## State And Persistence
No state is stored here. `atm_kptr_t` can represent live kernel VCC/session state in related protocols.

## Dependencies And Integration Points
Included by general ATM, signaling, LANE, MPOA, ATMTCP, and driver-private headers. It bridges ABI layout across architectures.

## Risks And Edge Cases
Alignment differences can break binary compatibility if omitted. The opaque pointer convention requires all-zero fields for NULL and no userspace dereference.

## Test Signals
Cross-architecture struct layout checks, NULL token handling, and round-trip tests in protocols using `atm_kptr_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmapi.h -->
