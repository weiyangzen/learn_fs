# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/Makefile.am

## Purpose
Delegates Commvault cloudsync plugin build to its `src` directory.

## Important APIs, types, and functions
Only `SUBDIRS = src`.

## Control flow
Recursive make enters the CVLT implementation directory when enabled.

## State and persistence behavior
No direct runtime state.

## Dependencies and integration points
Part of the conditional CVLT plugin build chain.

## Risks and test signals
Low risk. Verify it is included only under `BUILD_CVLT_PLUGIN`.
