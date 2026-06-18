# sources/distributed-fs/glusterfs/xlators/mgmt/Makefile.am

Purpose: top-level Automake dispatcher for management xlators. It delegates the `mgmt` subtree build to `glusterd`.

Important APIs/types/functions: `SUBDIRS = glusterd` and an empty `CLEANFILES` definition.

Control flow: Automake descends into `xlators/mgmt/glusterd` during build, install, and clean phases.

State and persistence behavior: no runtime state. Build state is limited to generated make artifacts in the build tree.

Dependencies and integration points: integrated by the parent GlusterFS Automake hierarchy; the existence of `glusterd/Makefile.am` is required.

Risks and edge cases: omitting additional management subdirectories here would exclude them from builds. Empty `CLEANFILES` is harmless but redundant.

Test signals: `make` traversal from the repository root and distribution tarball checks include the glusterd subtree.
