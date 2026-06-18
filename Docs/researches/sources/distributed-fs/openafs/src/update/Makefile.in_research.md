
# sources/distributed-fs/openafs/src/update/Makefile.in

This makefile builds the OpenAFS update service tools `upserver` and `upclient` and their rxgen-generated protocol support. It defines dependencies on auth, rx, rxkad, cmd, util, and opr libraries, and exposes `all`, `generated`, install, dest, and clean targets.

Generated artifacts come from `update.xg`: `update.cs.c`, `update.ss.c`, `update.xdr.c`, and `update.h`. `upclient` links `client.o`, client stubs, `utils.o`, and the common libraries; `upserver` links `server.o`, `utils.o`, server stubs, and the same library set. Object dependencies ensure `update.h`, `global.h`, and `AFS_component_version_number.c` are available.

Integration points are the top-level OpenAFS make configuration, pthread config, rxgen, libtool static linker rules, and server installation directories. Persistence behavior is build/install only: binaries land under server libexec or legacy destination paths.

Risks are mostly build-system drift: generated file dependencies must match rxgen outputs, clean must remove generated protocol files, and library ordering matters for static links. Test signals are `make generated`, full `make upclient upserver`, install/dest staging, and clean/regenerate idempotence.
