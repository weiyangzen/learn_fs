
# sources/distributed-fs/openafs/src/util/Makefile.in

Purpose: this makefile builds and installs OpenAFS utility libraries, exported utility headers, the `sys` program, generated `dirpath.h`, and utility tests.

Important targets and variables: `LT_objs` aggregates utility object files such as `base64`, time parsing, host parsing, logging, directory paths, atom list, linear hash, pthread lock, and tabular output. `all` builds headers, `util.a`, `libafsutil.a`, PIC/static variants, shared libtool libraries, `sys`, and tests. Install and dest targets copy headers and libraries into configured trees. `dirpath.h` is generated from `dirpath.hin` with configured installation paths. `check-splint` runs static analysis over key utility sources.

Control flow: dependency targets install generated/source headers under `${TOP_INCDIR}/afs`. Library targets use OpenAFS libtool macros for LWP, PIC, and shared builds. `test` delegates to the `test` subdirectory after library/header creation.

State and persistence: build outputs include generated headers, `.lo`/`.o`, archives, shared libraries, `sys`, and installed copies under build/dest prefixes.

Dependencies and integration: includes central OpenAFS config makefiles, LWP tooling, roken, thread libraries, `liboafs_opr`, version generation, and optional regex object.

Risks: header install lists and object lists must stay synchronized with source additions. `dirpath.h` generation uses `sed` with a quote delimiter and assumes configured paths do not contain that delimiter. Test signals include `make all`, `make test`, `make install DESTDIR=...`, `buildtools`, clean idempotence, and splint coverage when available.
