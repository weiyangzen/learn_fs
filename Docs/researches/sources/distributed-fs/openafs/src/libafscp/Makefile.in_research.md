<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/Makefile.in -->
# sources/distributed-fs/openafs/src/libafscp/Makefile.in

## Purpose
Builds and installs the static `libafscp.a` client-side AFS protocol helper library and its public header `afs/afscp.h`. The library wraps cell/server discovery, file, directory, volume, ACL, callback, and utility operations for lightweight AFS clients.

## Important APIs, Types, And Functions
The main variables are `LIBOBJS`, `KRB5CPPFLAGS`, object-specific `CFLAGS_afscp_util.o`, `CPPFLAGS_afscp_util.o`, and `CPPFLAGS_afscp_server.o`. Targets include `all`, `${TOP_LIBDIR}/libafscp.a`, `libafscp.a`, `depinstall`, `${TOP_INCDIR}/afs/afscp.h`, `install`, `dest`, and `clean`.

## Control Flow
Object files are archived with `AR` and indexed with `RANLIB`, then installed into the top build library directory. `depinstall` publishes the header and ensures component-version generation. Install/dest targets stage both the archive and public header.

## State And Persistence
Persistent outputs are `libafscp.a`, `AFS_component_version_number.c`, and installed headers/libraries. No runtime cache or callback state is changed by the makefile.

## Dependencies And Integration Points
It includes `Makefile.config`, `Makefile.pthread`, Kerberos CPP flags, `Makefile.version`, and source files in `src/libafscp`. The archive is consumed by utilities needing direct AFS file protocol access.

## Risks And Test Signals
Risks include missing objects from `LIBOBJS`, stale header installation, missing Kerberos flags for server/util code, and non-PIC/static-only assumptions. Test signals are a clean archive rebuild, installed header availability, and downstream links using `afscp_*` APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafscp/Makefile.in -->
