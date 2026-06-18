# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/Makefile.am

## Purpose
Builds the `cloudsync.la` xlator module, shared cloudsync common source, generated fop code, and plugin subtree.

## Important APIs, types, and functions
Defines `cloudsync_la_SOURCES = cloudsync.c cloudsync-common.c`, `nodist_cloudsync_la_SOURCES = cloudsync-autogen-fops.c cloudsync-autogen-fops.h`, and generation rules invoking `cloudsync-fops-c.py` and `cloudsync-fops-h.py` over template files. It defines `CS_PLUGINDIR` as an install-time plugin path used by `dlopen()` in `cloudsync.c`.

## Control flow
Automake first descends into `cloudsync-plugins`, generates the autogen C and H from Python scripts and templates, compiles the module with `LIB_DL`, and installs it under GlusterFS feature xlator directory. `uninstall-local` removes `cloudsync.so`.

## State and persistence behavior
Persists generated build outputs `cloudsync-autogen-fops.c` and `.h` during the build and cleans them through `CLEANFILES`.

## Dependencies and integration points
Depends on `libglusterfs`, dynamic loader support, GlusterFS RPC/XDR include paths, and Python generator infrastructure under `libglusterfs/src`. The plugin install path must match the plugin Makefiles that install `cloudsyncs3.so` and `cloudsynccvlt.so`.

## Risks and test signals
Risks include stale generated fops, missing Python generator modules, and mismatch between `CS_PLUGINDIR` and installed plugin names. Build tests should run from a clean tree, verify generated files are rebuilt, and confirm `cloudsync.la` links with `LIB_DL`.
