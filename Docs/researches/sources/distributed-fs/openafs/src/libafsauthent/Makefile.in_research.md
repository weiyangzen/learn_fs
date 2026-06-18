<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafsauthent/Makefile.in -->
# sources/distributed-fs/openafs/src/libafsauthent/Makefile.in

## Purpose
Builds the pthread-safe `libafsauthent` authentication/client support library by combining PIC/static OpenAFS audit, auth, kauth, ubik, sys, protection, volser, vlserver, opr, and util libraries with libafsrpc and crypto/roken/system libraries.

## Important APIs, Types, And Functions
Important make variables are libtool version fields `LT_current`, `LT_revision`, `LT_age`, `LT_objs`, `LT_deps`, `LT_libs`, optional `SHARED_LIBS`, and targets `libafsauthent.la`, `libafsauthent_pic.la`, `libafsauthent.a`, top-libdir archive installs, `install`, `dest`, and `clean`.

## Control Flow
`all` builds shared libraries when enabled, the PIC libtool archive, and static/PIC archives under `TOP_LIBDIR`. Shared linking uses `LT_LDLIB_shlib_only`; PIC and static archives use separate libtool invocations because AIX cannot produce both modes in one call. Install places shared/static artifacts in `${libdir}` and destination staging places the static archive in `${DEST}/lib`.

## State And Persistence
Persistent outputs are libtool archives, `.libs/libafsauthent_pic.a`, `libafsauthent.a`, and installed library files. No runtime authentication state is modified; this is build composition only.

## Dependencies And Integration Points
It includes `Makefile.config` and `Makefile.libtool`, depends on the listed component libraries and `libafsrpc`, and supplies a reusable auth/admin client library for other OpenAFS tools.

## Risks And Test Signals
Risks include libtool versioning mistakes, missing PIC variants, AIX shared/static behavior, dependency ordering, and shared-library install cleanup. Test signals are successful static/PIC/shared builds, correct exported symbols from `libafsauthent.la.sym`, install/dest staging, and downstream tool links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libafsauthent/Makefile.in -->
