# Research: sources/distributed-fs/lustre-release/lustre/ptlrpc/Makefile

## Purpose
This Makefile builds the Lustre `ptlrpc.o` kernel module. It composes the client/server PortalRPC core, security modules, llog networking, import/recovery machinery, network request scheduler pieces, LDLM object files, optional server target/nodemap code, optional GSS security subdirectory, and GCOV profiling flags.

## Important Build Variables
`obj-m += ptlrpc.o` declares the module. `ptlrpc_objs` lists core PTLRPC objects including `client.o`, `recover.o`, `connection.o`, `niobuf.o`, `pack_generic.o`, `service.o`, `pinger.o`, `import.o`, `ptlrpcd.o`, security implementations, NRS client pieces, `errno.o`, and `batch.o`.

`LDLM := ../ldlm/` and `TARGET := ../target/` are prefixes for imported object lists. The file includes `../ldlm/Makefile` unconditionally and `../target/Makefile` when `CONFIG_LUSTRE_FS_SERVER` is enabled. `nrs_server_objs` and `nodemap_objs` are appended only for server builds.

## Control Flow
The object list starts with always-built PTLRPC core files. It then imports LDLM objects through `$(patsubst %,$(LDLM)%,$(ldlm_objs))`, making LDLM part of the PTLRPC module link. In server configurations, it appends nodemap, server NRS, `pack_server.o`, `llog_server.o`, and target object files. `obj-$(CONFIG_LUSTRE_FS_GSS) += gss/` conditionally descends into the GSS security directory.

## State And Persistence
The Makefile does not maintain runtime state. Its effective state is build configuration: `CONFIG_LUSTRE_FS_SERVER`, `CONFIG_LUSTRE_FS_GSS`, and `CONFIG_GCOV_PROFILE_LUSTRE` change which objects and instrumentation are compiled. Because LDLM and optional target objects are folded into `ptlrpc.o`, symbol ownership and module init ordering are shaped by this file.

## Dependencies And Integration Points
This file integrates the PTLRPC directory with LDLM and target build fragments. `ccflags-y` adds include paths for `$(LUSTRE)/ldlm` and `$(LUSTRE)/target`, matching the cross-directory object linkage. Server builds depend on nodemap and target code being available and compatible with the PTLRPC module link.

## Risks
The unconditional LDLM include means errors or object list changes in the LDLM Makefile directly affect PTLRPC builds. Server conditional object additions can hide missing symbol problems until `CONFIG_LUSTRE_FS_SERVER` is enabled. Since `batch.o` is always included, client builds must compile its non-server fallback definitions correctly.

## Test Signals
Useful checks are client-only and server-enabled kernel builds, builds with `CONFIG_LUSTRE_FS_GSS`, builds with `CONFIG_GCOV_PROFILE_LUSTRE`, and link-time validation that imported LDLM/target object lists do not introduce duplicate objects or missing symbols.
