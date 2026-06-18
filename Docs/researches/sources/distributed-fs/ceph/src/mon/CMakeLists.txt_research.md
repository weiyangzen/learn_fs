<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CMakeLists.txt -->
# sources/distributed-fs/ceph/src/mon/CMakeLists.txt

## Purpose
This CMake file defines the static `mon` library for Ceph monitor code. It collects monitor services, Paxos code, auth handlers, capability parsers, and monitor subsystems into one link target consumed by the monitor daemon build.

## Important APIs, types, and functions
The relevant build variables are `lib_mon_srcs`, `HAVE_GSSAPI`, `WITH_JAEGER`, and the `mon` static library target. `lib_mon_srcs` lists core monitor implementation files including `Paxos.cc`, `PaxosService.cc`, `Monitor.cc`, `AuthMonitor.cc`, `ConfigMonitor.cc`, `Elector.cc`, `ElectionLogic.cc`, `ConnectionTracker.cc`, and several monitor services.

## Control flow
There is no runtime control flow. At configure/build time, CMake expands `lib_mon_srcs`, conditionally appends object files or Kerberos auth sources, creates `add_library(mon STATIC ...)`, and links common dependencies into the target.

## State and persistence behavior
The file has no runtime state or persistence. Its state is the static source graph and conditional target links. Build configuration flags determine whether `mgr_cap_obj`, Kerberos auth service handling, and Jaeger base support are included.

## Dependencies and integration points
The target links `legacy-option-headers`, `kv`, `heap_profiler`, `${FMT_LIB}`, and optionally `jaeger_base`. It reaches outside `src/mon` for auth, MDS, MGR, and OSD capability code, reflecting that monitor command/auth handling depends on those cap parsers.

## Risks and edge cases
Build skew is the main risk: adding a monitor source or moving symbols requires keeping `lib_mon_srcs` synchronized. Optional sources guarded by `HAVE_GSSAPI`, `mgr_cap_obj`, or `WITH_JAEGER` must be available only when their targets/options exist. Since this target is static, missing source entries become link-time unresolved symbols in downstream binaries.

## Test signals
Build tests should cover default monitor builds, GSSAPI-enabled builds, Jaeger-enabled builds, and builds with or without `mgr_cap_obj`. A clean link of the monitor daemon is the primary validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mon/CMakeLists.txt -->
