<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxosd/Makefile.in -->
# sources/distributed-fs/openafs/src/rxosd/Makefile.in

## Purpose

This makefile drives the rxosd build, including generated Rx RPC sources, the `rxosd` server binary, the `osd` command/client utility, the `readabyte` helper, and the static `librxosd.a` client/XDR library installed into the top-level library directory. It is a configure-template makefile that includes OpenAFS build configuration and pthread settings.

## Important Targets and Variables

Important directory variables point to sibling OpenAFS components: `VICED`, `VLSERVER`, `LWP`, `LIBACL`, `UTIL`, `DIR`, `VOL`, `OSDDBSRC`, and `FSINT`. `HSM_LIB` and `HSM_INC` are configure substitutions for external HSM integration, and `PNFS_OPT` is used in several rxosd-related compile flags.

Object groups define build composition:

- `RXOSDOBJS`: rxosd service/client generated files plus rxosd HSM and dcache objects.
- `LWPOBJS`, `UTILOBJS`, `VOLOBJS`, and `OSDDBOBJS`: local copies of common OpenAFS objects needed by this server.
- `LIBS`: authentication, RPC, util, and command libraries from `${TOP_LIBDIR}`.

Generated interface targets use `RXGEN` on `rxosd.xg` and `../osddb/osddb.xg`:

- `rxosd.h`, `rxosd.ss.c`, `rxosd.cs.c`, `rxosd.xdr.c`
- kernel-style variants `Krxosd.cs.c`, `Krxosd.xdr.c`
- `osddb.h`, `osddb.cs.c`, `osddb.xdr.c`

Build products include `osd`, `rxosd`, `readabyte`, `librxosd.a`, and `${TOP_INCDIR}/afs/rxosd.h`.

## Control Flow

The default `all` target generates rxosd client/XDR files and the exported header, then builds and installs `librxosd.a` into `${TOP_LIBDIR}`. The `rxosd` target links the service binary from generated rxosd objects plus common LWP/util/vol/osddb objects and HSM libraries. The `osd` target links the command utility against rxosd client stubs, osddb user code, policy parser output, and shared OpenAFS libs. `readabyte` links a small helper against HSM/dcache-related objects.

Compilation rules pull source from sibling directories using `${AFS_CCRULE}`. The `policies.tab.c` rule invokes `${YACC}` on `policies.y`; `policy_parser.o` depends on that generated parser but appears to compile `policy.tab.c`, which is suspicious because the generator target name is `policies.tab.c`.

`install` installs server executables under `${afssrvlibexecdir}`, the `osd` command under `${bindir}`, and the exported rxosd header/library through other targets. `dest` installs into legacy `${DEST}` packaging paths. `clean` removes generated rxosd/osddb files, object files, policy parser output, and component version files.

## State and Persistence Behavior

The makefile persists generated C/header files, object files, static libraries, executables, and installed headers/binaries. It does not manage runtime rxosd state. Build output location is split between the local directory, `${TOP_INCDIR}`, `${TOP_LIBDIR}`, `${DESTDIR}`, and `${DEST}`.

## Dependencies and Integration Points

This file integrates rxosd with Rx RPC generation (`RXGEN`), OpenAFS auth/RPC/cmd/util libraries, volume-server support code, osddb generated stubs, yacc-generated policy parsing, HSM libraries, and pthread settings. It also reuses low-level volume/namei code with `-DBUILDING_RXOSD` and HSM/pNFS compile flags.

## Risks and Edge Cases

There is a likely typo in the `install` target: `${DESTDIR}}${afssrvlibexecdir}/rxosd` contains an extra `}` and can install `rxosd` to a malformed path. The `policy_parser.o` rule depends on `policies.tab.c` but compiles `policy.tab.c`, while `clean` removes `policy_parser.c`; these names should be validated against the actual yacc output and parser source naming. Duplicate `dest` target definitions appear: an early `dest: all` and a later install-style `dest:` rule. In make, multiple rules can merge prerequisites/recipes depending on syntax, but duplicate target recipes are risky and may warn or override behavior.

Because the makefile compiles many objects from sibling directories with rxosd-specific flags, stale objects or flag mismatches can produce subtle ABI differences. Generated RPC files must be regenerated when `.xg` interfaces change, and clean rules must remove all generated names consistently.

## Test Signals

Run `make generated`, `make all`, and target-specific builds for `rxosd`, `osd`, `readabyte`, and `librxosd.a`. Validate install paths with `make -n install DESTDIR=/tmp/stage`. Check yacc parser generation names with a dry run. Packaging tests should verify `${TOP_INCDIR}/afs/rxosd.h`, `${TOP_LIBDIR}/librxosd.a`, server binaries, and user command placement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/rxosd/Makefile.in -->
