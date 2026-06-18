# sources/distributed-fs/openafs/src/rxkad/test/Makefile.in

Purpose: Automake-style makefile template for rxkad stress and fcrypt tests.

Important targets: `all`, `test`, and `system` build `stress`, `th_stress`, and `fc_test`. RXGEN rules generate `stress.ss.c`, `stress.cs.c`, `stress.xdr.c`, and `stress.h` from `stress.rg`. Error-table rules generate `stress_errs.c/h`. Separate LWP and pthread link lines build legacy and threaded stress binaries.

Control flow and state: Build orchestration only. `clean` removes generated RPC stubs, error files, binaries, and objects. `fc_test.o` adds rxkad include paths.

Dependencies and integration: Links auth, rx, lwp, cmd, rxkad, hcrypto, com_err, util, opr, rfc3961, roken, pthread, and generated RPC/error sources.

Risks: Generated source dependencies must be correct or stale stubs can mask interface changes. Library order is significant for legacy static linking.

Test signals: Successful `stress`, `th_stress`, and `fc_test` builds provide compile/link coverage for rxkad core, test RPCs, and hcrypto integration.
