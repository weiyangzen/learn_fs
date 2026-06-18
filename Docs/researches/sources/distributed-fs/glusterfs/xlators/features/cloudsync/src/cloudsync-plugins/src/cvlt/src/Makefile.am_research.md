# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/cvlt/src/Makefile.am

## Purpose
Builds the `cloudsynccvlt.la` Commvault cloudsync plugin module.

## Important APIs, types, and functions
Defines plugin sources as `libcvlt.c` plus shared `cloudsync-common.c`, noinst headers for archive store and CVLT types/messages, and exports symbols from `libcloudsynccvlt.sym`.

## Control flow
Compiles and installs the module under the shared cloudsync plugin directory, where `cloudsync.c` can load `cloudsynccvlt.so` for plugin name `cvlt` on Linux.

## State and persistence behavior
Build artifact is the CVLT plugin shared object.

## Dependencies and integration points
Depends on `libglusterfs`, GlusterFS include trees, and an external runtime `libopenarchive.so` loaded by the plugin implementation.

## Risks and test signals
Risks include symbol export mismatch and runtime dependency not present despite successful build. Tests should build with `BUILD_CVLT_PLUGIN`, inspect exported `store_ops`, and run plugin init with and without `libopenarchive.so`.
