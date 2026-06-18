<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/modules-check.sh -->
# sources/distributed-fs/ceph-client/scripts/modules-check.sh

## Purpose

`modules-check.sh` validates module install/order metadata for duplicate module names that would collide after installation.

## Important APIs, Types, and Functions

The script operates on module list files such as `modules.order`, converting object paths to `.ko` names and checking basenames.

## Control Flow

It reads module paths, normalizes them, sorts or groups by basename, and reports duplicate module names as errors.

## State and Persistence Behavior

It is read-only and exits non-zero when duplicates are found.

## Dependencies and Integration Points

It depends on POSIX shell and core text utilities. It integrates with Kbuild module checks before packaging or installation.

## Risks and Edge Cases

Only name-level collisions are detected; semantic conflicts or aliases are outside scope. Generated or externally supplied module lists must be current. Path normalization must match install naming.

## Test Signals

Feed module lists with unique modules, same basename in different directories, empty lists, and paths already ending in `.ko`. Confirm duplicate diagnostics and exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/modules-check.sh -->
