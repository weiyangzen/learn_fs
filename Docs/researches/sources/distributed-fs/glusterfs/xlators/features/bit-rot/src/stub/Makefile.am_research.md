# sources/distributed-fs/glusterfs/xlators/features/bit-rot/src/stub/Makefile.am

Purpose: this Automake file builds the `bitrot-stub` xlator when server support is enabled. It installs the module under the GlusterFS feature xlator directory and declares the C sources and private headers for the bit-rot stub.

Important build declarations: `xlator_LTLIBRARIES = bitrot-stub.la` is guarded by `WITH_SERVER`. `bitrot_stub_la_SOURCES` includes `bit-rot-stub-helpers.c` and `bit-rot-stub.c`. `noinst_HEADERS` lists `bit-rot-stub.h`, `bit-rot-common.h`, `bit-rot-stub-mem-types.h`, `bit-rot-object-version.h`, and `bit-rot-stub-messages.h`. The target links against `libglusterfs.la`.

Control flow and integration: the file has no runtime control flow, but it controls whether the stub xlator is part of the server-side translator set. Include paths cover libglusterfs, XDR generated headers, and RPC libraries, matching the stub's use of GlusterFS fop, xdr, and system wrappers.

State and persistence behavior: none directly. Its build output enables the runtime code that persists bitrot version and signature xattrs and maintains the quarantine directory.

Dependencies and risks: dependency risks are mostly build-time. Missing RPC/XDR include paths or a server-disabled build will prevent the stub from compiling or installing. Because `bit-rot-common.h` is shared with the daemon, this build file must stay in sync with any header split or rename.

Test signals: `make` with `WITH_SERVER` should produce `bitrot-stub.la`; distribution checks should include all noinst headers and avoid missing generated XDR include paths.
