# sources/distributed-fs/lizardfs/src/nfs-ganesha/CMakeLists.txt

## Purpose
Builds the LizardFS NFS-Ganesha FSAL plugin as a module named `fsallizardfs`.

## Important APIs, Types, And Functions
Uses `collect_sources(NFS_GANESHA_PLUGIN)`, includes external Ganesha and NTIRPC headers, links the module against `lizardfs-client_pic`, and installs it under `${LIB_SUBDIR}/ganesha` in the `fsal` component.

## Control Flow
CMake collects plugin sources, creates a `MODULE` library from `${NFS_GANESHA_PLUGIN_MAIN}` and `${NFS_GANESHA_PLUGIN_SOURCES}`, then wires the LizardFS client PIC library.

## State And Persistence Behavior
No runtime state. It defines build/install topology for the plugin artifact.

## Dependencies And Integration Points
Depends on external source variables `NFS_GANESHA_DIR_NAME` and `NTIRPC_DIR_NAME`, the local source collector macros, and the LizardFS client library.

## Risks And Edge Cases
Header path compatibility is tied to the vendored/external Ganesha and NTIRPC layouts. Missing PIC client library or changed external include trees will break plugin builds.

## Test Signals
Build success of `fsallizardfs` and any Ganesha FSAL/plugin tests are the primary signals.
