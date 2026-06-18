# sources/distributed-fs/glusterfs/xlators/features/cloudsync/src/cloudsync-plugins/src/Makefile.am

## Purpose
Selects optional cloudsync plugin subdirectories based on configure-time feature flags.

## Important APIs, types, and functions
If `BUILD_AMAZONS3_PLUGIN` is set, `AMAZONS3_DIR = cloudsyncs3`; if `BUILD_CVLT_PLUGIN` is set, `CVLT_DIR = cvlt`; `SUBDIRS` expands to those enabled directories.

## Control flow
Automake builds only configured plugin directories, allowing cloudsync core to compile without plugin dependencies.

## State and persistence behavior
No runtime state. Build output is controlled indirectly by selected subdirectories.

## Dependencies and integration points
Couples configure flags to plugin modules that cloudsync later loads by name from `CS_PLUGINDIR`.

## Risks and test signals
Risk is deployment mismatch: a volume can request a plugin not built or installed. Tests should cover builds with neither, each, and both plugin flags.
