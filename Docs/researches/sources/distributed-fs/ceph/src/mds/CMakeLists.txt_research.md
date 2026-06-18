# sources/distributed-fs/ceph/src/mds/CMakeLists.txt

## Purpose
This CMake file defines the `mds` static library for Ceph's Metadata Server implementation. It collects the MDS source files that implement server request handling, metadata cache objects, journaling, migration, balancing, locks, snap handling, sessions, metrics, quiesce logic, and related common components.

## Important Build APIs And Targets
The file sets `mds_srcs` with local MDS implementation files including `Capability.cc`, `MDSDaemon.cc`, `MDSRank.cc`, `Server.cc`, `Mutation.cc`, `MDCache.cc`, `CDentry.cc`, `CDir.cc`, `CInode.cc`, lock classes, snap classes, table clients/servers, scrub, damage, metrics, and quiesce components. It also includes shared sources from `src/common`, `src/osdc`, and `src/mgr` such as `TrackedOp.cc`, `MemoryModel.cc`, `Journaler.cc`, and `MDSPerfMetricTypes.cc`.

The build creates `add_library(mds STATIC ${mds_srcs})`. It links privately against `legacy-option-headers`, `Boost::url`, profiler libraries, `osdc`, and `${LUA_LIBRARIES}`. It adds the Lua include directory privately with `target_include_directories(mds PRIVATE "${LUA_INCLUDE_DIR}")`.

## Control Flow And Integration
There is no runtime control flow in this file, but it is the compilation integration point for the MDS implementation. Adding `Capability.cc` and `CInode.cc` here ensures their object code is part of the static library consumed by the Ceph MDS daemon. The local list makes source membership explicit rather than using globbing, so adding a new `.cc` file in `src/mds` requires updating this list.

## State And Persistence Behavior
The file does not define persistent state directly. Its choices affect which persistence implementations are compiled into the MDS library: inode store/backtrace persistence from `CInode.cc`, directory OMAP persistence from `CDir.cc`, journal behavior from `MDLog.cc` and `journal.cc`, and table persistence through `InoTable.cc`, `MDSTable*`, and snap table sources.

## Dependencies And Risks
The target depends on external imported targets and variables being configured by parent CMake files. Missing Lua variables, profiler targets, Boost URL, or `osdc` linkage will break MDS builds. Because the file uses private linkage/includes, consumers of `mds` should not rely on Lua headers or these private libraries leaking transitively. The explicit source list is easy to audit but has omission risk when new implementation files are added.

## Test Signals
Primary signals are configure-time success, `mds` target compilation, full MDS unit/integration test builds, and link success for binaries that consume the static library. Build-system tests should catch missing source entries by unresolved symbols or missing behavior in MDS test targets.
