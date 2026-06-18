# sources/distributed-fs/openafs/src/opr/Makefile.in

Purpose: build/install rules for OpenAFS portable runtime (`opr`) library and exported headers.

Important APIs/types/functions: builds libtool objects for assert, cache, string case helpers, dict, fmt, proc, rbtree, softsig, threadname, and uuid. Produces `liboafs_opr.la`, static `libopr.a`, PIC archive, and installed headers under `afs/` and `opr/`.

Control flow: `all` installs headers into the top include directory and builds libraries. Header targets copy source headers to canonical public names, including `opr_lock.h` to `opr/lock.h` and `opr_time.h` to `opr/time.h`. `install`, `dest`, and `buildtools` provide build-system integration.

State and persistence: creates build artifacts, installed libraries, and copied headers.

Dependencies/integration: includes OpenAFS config make fragments for pthreads and libtool. Links with hcrypto and roken libraries.

Risks and test signals: installed header names are part of the public contract. Missing copy targets break downstream includes. Build and link coverage are the main validation signals.
