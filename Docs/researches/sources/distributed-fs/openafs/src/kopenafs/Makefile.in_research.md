## sources/distributed-fs/openafs/src/kopenafs/Makefile.in

Purpose: this makefile builds and installs `libkopenafs`, a small standalone OpenAFS syscall/pioctl compatibility library and header.

Important targets: `all` builds shared/static `libkopenafs` and installs `kopenafs.h` into the top include directory. `LT_objs` include `glue`, `pioctl`, `setpag`, `kopenafs`, and version object. Foreign source build rules compile code from `../sys`. `syscall.lo` handles platform-specific syscall assembly for SGI, AIX, HP-UX, or creates an empty object fallback. Test targets build `test-unlog` and `test-setpag` statically against `libkopenafs.a`.

State and persistence: build artifacts are libraries, libtool metadata, installed headers, test binaries, and generated version/syscall objects.

Dependencies and integration points: depends on config, libtool, pthread make fragments, sys syscall sources, `libkopenafs.la.sym`, and install variables. It exposes a library intended for Heimdal/KTH `libkafs` compatibility.

Risks: the comment notes foreign implicit rules do not work because sources live elsewhere. Platform-specific syscall assembly paths are fragile and rely on `SYS_NAME`. Shared-library installation removes `.la` files after libtool install.

Test signals: successful build of `libkopenafs.a`/shared library and optional `test-setpag`/`test-unlog` binaries; runtime tests require a native AFS client.
