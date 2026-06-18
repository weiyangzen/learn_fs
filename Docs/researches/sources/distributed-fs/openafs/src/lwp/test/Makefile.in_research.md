# sources/distributed-fs/openafs/src/lwp/test/Makefile.in

Purpose: build rules for LWP test binaries.

Important APIs/types/functions: targets `test`, `selclient`, `selserver`, `test_key`, and `rw`. It compiles shared `selsubs.o` for select tests and links `rw` with `libopr.a` in addition to `liblwp.a`.

Control flow: normal make dependency graph. `all` builds every test. Clean removes objects, archives, binaries, and core files.

State and persistence: produces local test binaries and object files. No runtime state.

Dependencies/integration: includes OpenAFS config make fragments `Makefile.config` and `Makefile.lwp`, uses `AFS_LDRULE`, `XLIBS`, `DESTDIR` includes, `TOP_LIBDIR`, and `../liblwp.a`.

Risks and test signals: the test set is the main signal for LWP behavior. Missing `XLIBS` or `libopr.a` will break selected targets. The makefile itself has low logic risk but depends on generated config variables.
