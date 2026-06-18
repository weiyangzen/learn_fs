# sources/distributed-fs/openafs/src/cmd/test/Makefile.in

Purpose: builds three small command parser test binaries: `ctest`, `dtest`, and `itest`.

Important targets: `test`/`tests` depend on all three binaries. Each binary links its object with `-lcmd`, `libafscom_err.a`, `-lafsutil`, roken, and platform libraries. `clean` removes objects, binaries, archives, and core files.

Dependencies and integration: includes common config and LWP make fragments, and expects `libcmd` and generated `<afs/cmd.h>` to be available from the parent build.

Risks and tests: there is no scripted expected-output validation; the target only builds runnable examples. `install` and `dest` are empty, keeping these as build-tree tests.
