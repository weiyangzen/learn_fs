<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile.am -->
## sources/cloud-native/ostree/Makefile.am

### Purpose
This is the top-level non-recursive automake file that assembles OSTree's build graph from fragments, global flags, bundled dependencies, release targets, and distribution helpers.

### APIs, Types, and Control Flow
It includes `Makefile-decls.am`, sets path/version defines, warning flags, distcheck configure defaults, gitignore files, and package dependency variables. It conditionally includes introspection make rules and the `apidoc` subdir. It includes generated libglnx and bsdiff fragments, then project fragments for otutil, otcore, libostree, CLI, switchroot, tests, boot, manpages, and bash completion. Release targets create git tags, embedded-dependency tarballs, and a `dist-then-build` smoke build from a generated dist archive.

### State, Dependencies, and Integration
It coordinates generated files, submodules, `EXTRA_DIST`, `CLEANFILES`, install hooks, and recursive doc builds. Release tarball logic archives the current revision, submodules, and selected embedded dependencies.

### Risks and Test Signals
Include order is critical because fragments append to variables initialized early. Release-tarball logic shells through git and tar and depends on submodule state. Test signals are autoreconf/configure, full make, distcheck-like builds, embedded tarball generation, and package CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile.am -->
