# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.h

## Purpose
Shared DEXCR declarations, aspect metadata, and raw hash instruction encodings.

## Important APIs, Types, and Functions
Defines DEXCR bit macros, `PPC_RAW_HASHST`, `PPC_RAW_HASHCHK`, `struct dexcr_aspect`, `aspects[]`, `enum dexcr_source`, and prototypes for all DEXCR helper functions.

## Control Flow
No runtime control flow, but macro expansion emits raw instructions and aspect table iteration drives the utilities/tests.

## State and Persistence
The static `aspects[]` table is read-only process data. DEXCR state is accessed through declared helpers.

## Dependencies and Integration Points
Depends on prctl constants and `reg.h` bit helpers. Included by every DEXCR test/tool.

## Risks and Test Signals
Risk is aspect table drift from kernel ABI or incorrect bit numbering. Build failures or prctl/hash tests reveal mismatches.
