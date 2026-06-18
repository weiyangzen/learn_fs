<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/userspace-api/media/conf_nitpick.py -->
# sources/distributed-fs/ceph-client/Documentation/userspace-api/media/conf_nitpick.py

## Purpose
Sphinx configuration fragment for building Linux media userspace API documentation in nitpicky mode while suppressing known unresolved C references that are expected or outside the current documentation set.

## Important APIs, Types, And Functions
- `project` identifies the documentation project.
- `nitpicky = True` enables strict unresolved-reference reporting.
- `intersphinx_mapping = {}` disables external intersphinx resolution for this nitpick build.
- `nitpick_ignore` lists `(domain:role, target)` tuples for C functions and C types.

## Control Flow
Sphinx imports this file as configuration. Nitpicky mode then reports unresolved references unless they match an entry in `nitpick_ignore`. There is no executable control flow beyond module import.

## State And Persistence
The file only defines configuration variables. It writes no state and has no runtime persistence beyond the Sphinx build process.

## Dependencies And Integration Points
Integrates with Sphinx's nitpicky reference checking and the C domain. The ignore list reflects media documentation references to libc calls, kernel helpers, typedefs, opaque structs, and symbols documented in other books or not yet converted to ReST.

## Risks And Edge Cases
The ignore list can hide real documentation regressions if entries are too broad or stale. Duplicate entries such as `pollfd` and `timeval` add maintenance noise. Disabling intersphinx ensures local strictness but prevents legitimate cross-project resolution.

## Test Signals
Run the media docs nitpick build and verify that only actionable unresolved references remain. Remove one ignored symbol in a controlled test to confirm Sphinx reports it, and periodically prune entries that become documented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/userspace-api/media/conf_nitpick.py -->
