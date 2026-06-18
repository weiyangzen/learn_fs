<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/Makefile.in -->
# sources/distributed-fs/openafs/src/libadmin/samples/Makefile.in

## Purpose
Builds the libadmin sample command programs for cache-manager, RX debug, and RX statistics APIs. It is an Autoconf template that pulls in OpenAFS build configuration and pthread settings, links each sample statically against the admin and RPC libraries, and installs the RX statistics sample tools.

## Important APIs, Types, And Functions
`SAMPLEPROGS` enumerates the 21 sample binaries. `SAMPLELIBS` links admin utility, client, vos, bos, afsrpc, auth, kauth, cmd, util, ubik, opr, and crypto support libraries. Individual targets use `$(LT_LDRULE_static)` with roken, crypt, and pthread libraries. `CFLAGS_rxstat_query_peer.o` and `CFLAGS_rxstat_query_process.o` opt those objects out of warnings-as-errors.

## Control Flow
`all`, `test`, and `tests` build all sample programs. Each program target depends on its object and shared sample libraries. `install` places only the `rxstat_*` tools into `${sbindir}`; `dest` installs those same tools into `${DEST}/etc`; `clean` removes libtool products, objects, binaries, and core files.

## State And Persistence
The makefile creates build outputs in the sample directory and installs selected binaries. It does not generate runtime state.

## Dependencies And Integration Points
It depends on top-level configured variables such as `TOP_LIBDIR`, `TOP_OBJDIR`, `LIB_roken`, `LIB_crypt`, `MT_LIBS`, and install paths. It integrates sample programs with the broader OpenAFS libadmin, RX, ubik, command-parser, and crypto libraries.

## Risks And Test Signals
Risks include stale library ordering, missing new sample programs in install lists, and warning suppressions masking real query-sample type issues. Test signals are successful `make all`, `make install DESTDIR=...`, and execution of representative CM, rxdebug, and rxstat samples against a test service.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/Makefile.in -->
