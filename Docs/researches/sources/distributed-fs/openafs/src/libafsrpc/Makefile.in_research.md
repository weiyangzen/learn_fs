## sources/distributed-fs/openafs/src/libafsrpc/Makefile.in

Purpose: Builds the `libafsrpc` aggregate RPC library in static, PIC archive, and optional shared forms.

Important targets and variables: `LT_current`, `LT_revision`, and `LT_age` define libtool versioning. `LT_objs` aggregates fsint, rx, rxkad, crypto, comerr, util, rxstat, sys, lwp compatibility, opr, and optional rxgk libraries. `LT_libs` includes hcrypto, roken, threading, and optional GSSAPI libs. Targets include `all`, `libafsrpc.la`, `libafsrpc_pic.la`, `libafsrpc.a`, top libdir install rules, `install`, `dest`, and `clean`.

Control flow: `all` builds shared libraries when configured plus static and PIC archives. The shared-library rule links with `LT_LDLIB_shlib_only_NOQ`, with an AIX-specific branch adding the syscall import list `../sys/afsl.exp`. Static archive creation also adds `afsl.exp` on AIX. Install and dest targets place archives and optional shared artifacts in configured lib directories, then remove installed `.la` files for shared installs.

State and persistence: Produces build artifacts in the object tree and installs them to top libdir, DESTDIR libdir, or DEST lib. No runtime state.

Dependencies and integration: Integrates many lower-level OpenAFS libraries into a consumable RPC library. Conditional rxgk support is injected by configure substitutions.

Risks: Aggregate link order and platform-specific import-list handling are fragile. The `.libs/libafsrpc_pic.a` path assumes libtool internals. Libtool version increments require maintainer discipline.

Test signals: Build on AIX and non-AIX, shared and static configurations, rxgk enabled and disabled, install/dest packaging, and consumers linking against both `libafsrpc.a` and `libafsrpc_pic.a`.
