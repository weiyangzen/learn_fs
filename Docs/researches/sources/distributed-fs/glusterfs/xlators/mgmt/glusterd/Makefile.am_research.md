# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/Makefile.am

Purpose: Automake dispatcher for the glusterd management translator subtree.

Important APIs/types/functions: `SUBDIRS = src` and empty `CLEANFILES`.

Control flow: build/install/clean traversal descends into `xlators/mgmt/glusterd/src`, where the actual translator module is defined.

State and persistence behavior: no runtime state.

Dependencies and integration points: depends on `src/Makefile.am`; included by `xlators/mgmt/Makefile.am`.

Risks and edge cases: any new glusterd subdirectories must be added here or they will be skipped by Automake recursion.

Test signals: full Automake build traversal and `make distcheck`.
