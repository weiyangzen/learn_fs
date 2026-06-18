# sources/distributed-fs/openafs/src/platform/IRIX/Makefile.in

## Purpose
Builds IRIX authentication interposition shared libraries for remote shell/login integration. It links `sgi_auth.o` with AFS authentication libraries and helper objects (`ta-rauth.o`, `rcmd.o`, `herror.o`) to produce `afsauthlib.so` and Kerberos-flavored `afskauthlib.so`.

## Important APIs, Types, And Functions
Key variables are `AFSLIBS`, `KAFSLIBS`, `AUTHFILES`, `AUTHLIBS`, and `TARGETS`. Build products are installed into `${TOP_LIBDIR}` for in-tree use, `${DESTDIR}${libdir}` for install, or `${DEST}/root.client/usr/vice/etc` for legacy destination staging.

## Control Flow
`all` builds both shared libraries in the top library directory. The local shared-library targets invoke `$(LD) -shared -all` with either normal or Kerberos auth libraries. `install` and `dest` stage both libraries. Object rules are simple source-to-object dependencies.

## State And Persistence
Build state includes helper objects and the two `.so` files. Install/dest state persists shared libraries where IRIX client authentication mechanisms can load them.

## Dependencies And Integration Points
Depends on LWP-era OpenAFS libraries: kauth, prot, ubik, auth, rxkad, sys, rx, crypto, lwp, cmd, com_err, and util. Integrates IRIX login/rsh authentication paths with AFS tokens through `sgi_auth.c`, `ta-rauth.c`, and `rcmd.c`.

## Risks And Test Signals
Risks include very old IRIX linker flags, static library ordering, Kerberos/non-Kerberos variant drift, and the possibility that installing these libraries changes login behavior. Test signals are successful IRIX link, exported symbols expected by the OS authentication loader, and validated authenticated/unauthenticated remote login behavior.
