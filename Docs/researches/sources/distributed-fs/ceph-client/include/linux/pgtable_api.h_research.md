# sources/distributed-fs/ceph-client/include/linux/pgtable_api.h

## Purpose
Compatibility include that exposes the generic page-table API by including `<linux/pgtable.h>`. It contains no independent declarations or logic.

## Important APIs, Types, and Functions
All exported API surface comes from `linux/pgtable.h`, including page-table walking, PTE mutation, huge-page, pgprot, and page-table synchronization helpers.

## Control Flow
No runtime control flow. Preprocessor inclusion delegates entirely to `pgtable.h`.

## State and Persistence
No owned state. Any page-table state affected by users of this header is managed by the APIs included from `pgtable.h`.

## Dependencies and Integration Points
Integrates consumers that include `pgtable_api.h` with the canonical page-table header. Its only dependency is `linux/pgtable.h`.

## Risks
The risk is only aliasing or include-order confusion if future code expects this file to define a separate API boundary. It should stay a thin wrapper unless callers are migrated.

## Test Signals
Build coverage for files including `linux/pgtable_api.h` is the primary signal; failures would be missing declarations from the delegated include.
