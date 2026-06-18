# sources/distributed-fs/glusterfs/xlators/performance/Makefile.am

## Purpose
Defines the automake traversal order for the GlusterFS performance translator family. It causes build/install recursion into write-behind, read-ahead, readdir-ahead, io-threads, io-cache, quick-read, md-cache, open-behind, and nl-cache.

## Important APIs, types, and functions
There are no C APIs. `SUBDIRS` is the significant build interface because it controls which translator modules are included in the performance xlator subtree. `CLEANFILES` is present but empty.

## Control flow
During `make`, automake recurses into the listed directories. io-threads, io-cache, and md-cache build rules in this subset are reachable only because they appear in this parent list.

## State and persistence behavior
No runtime state is involved. The persistent behavior is build/install inclusion in generated makefiles.

## Dependencies and integration points
Integrates with the top-level autotools build and package layout for `xlator/performance` modules. Adding or removing a performance translator requires this list to remain consistent with the child directory and volfile expectations.

## Risks and test signals
Risks are build omissions, install omissions, and stale subdirectory names. Test signals are successful `make` recursion, packaged `.so` files for each listed translator, and `make distcheck` catching missing or renamed subdirectories.
