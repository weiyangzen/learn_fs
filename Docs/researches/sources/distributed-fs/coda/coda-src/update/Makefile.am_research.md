# sources/distributed-fs/coda/coda-src/update/Makefile.am

Purpose: Automake build rules for the Coda update service programs and RPC2-generated stubs.

Important declarations: under `BUILD_SERVER`, builds `updateclnt`, `updatefetch`, and `updatesrv` as `sbin_PROGRAMS` and installs `updateclnt.8`/`updatesrv.8`. `RPC2_FILES = update.rpc2` plus `rpc2_rules.mk` generates client/server/helper sources and `update.h`. Each program has a hand-written source plus `nodist_*` generated RPC2 files. `AM_CPPFLAGS` adds RPC2, base, util, and vicedep include paths. `LDADD` links vice errors, volutil dependencies, util, base, and RPC2 libraries.

Control flow/state: build-time only. It controls generated source inclusion and link dependencies for the update protocol.

Dependencies, risks, tests: depends on RPC2 code generation and top-level build products. Risks include generated-source dependency ordering, all three programs sharing broad link dependencies, and no installed manpage for `updatefetch`. Test clean builds from generated-free tree, `make distcheck`, server-disabled builds, and relinking after `update.rpc2` changes.
