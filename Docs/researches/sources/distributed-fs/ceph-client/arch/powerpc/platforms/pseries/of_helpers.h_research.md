# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/of_helpers.h

## Purpose
Declares the pSeries OF helper interface for deriving a parent device node from a full OF path.

## Important APIs, Types, And Functions
Includes `<linux/of.h>` and declares `struct device_node *pseries_of_derive_parent(const char *path);`.

## Control Flow
This header has no runtime control flow. It allows other pSeries compilation units to call the implementation in `of_helpers.c`.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on Linux OF types and is integrated by pSeries code that needs to create or reparent dynamic device-tree nodes.

## Risks And Edge Cases
The header does not declare `of_read_drc_info_cell` even though `of_helpers.c` defines and exports it; that API is presumably declared in broader PowerPC OF headers. Include guard prevents duplicate declarations.

## Test Signals
Compile coverage is the useful signal: users of `pseries_of_derive_parent` should include this header without missing-type warnings or duplicate definitions.
