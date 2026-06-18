# sources/distributed-fs/ceph/src/librados/CMakeLists.txt

## Purpose
`CMakeLists.txt` builds the internal and public librados targets.

## Important APIs, Types, and Functions
It creates static `librados_impl` from `IoCtxImpl.cc`, `RadosXattrIter.cc`, `RadosClient.cc`, `librados_util.cc`, and `librados_tp.cc`, linked with `legacy-option-headers`. It creates shared/static `librados` from C and C++ API translation units plus common buffer objects.

## Control Flow
When shared libraries are enabled, it sets output name `rados`, version `2.0.0`, soversion `2`, hidden inline visibility, optional exclude-libs and version-script linker flags, optional static libstdc++/gcc flags, and `LIBRADOS_SHARED=1`. It links `librados` with implementation, osdc, ceph-common, cls lock client, and platform crypto/block/GSS/external libraries. It installs the target and adds tracing dependencies when LTTng/eventtrace are enabled.

## State and Persistence Behavior
No runtime state. Build output artifacts and install targets are produced by CMake.

## Dependencies and Integration Points
This file integrates librados with Ceph's build options and tracepoint generation. Public API files depend on private `librados_impl`.

## Risks
Link flags are platform-guarded; version scripts and exclude-libs must remain compatible with non-Windows shared builds. Missing trace dependencies can break eventtrace-enabled builds.

## Test Signals
Build matrix signals include shared/static builds, eventtrace/LTTng builds, versioned symbol exports, and installation path correctness.
