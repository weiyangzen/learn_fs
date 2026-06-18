# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-sigreturn.c

Purpose: verifies sigreturn from inside a suspended transaction reclaims/discards the transaction before restoring TM SPRs.

Important APIs/types/functions: `handler()` starts/suspends a transaction in the SIGSEGV handler; `tm_sigreturn()` triggers SIGSEGV inside an active transaction and checks abort-path return code.

Control flow: the main test installs a SIGSEGV handler, begins a transaction, stores to address zero to fault, and expects signal handling plus sigreturn to abort the transaction. The final `ret` value must be 2 from the abort handler path.

State and persistence behavior: local `ret` communicates assembly path outcome; no external state.

Dependencies and integration points: requires real HTM and ppc64le.

Risks and test signals: normal transaction continuation after fault is failure. The test exits explicitly with success/failure rather than returning normally from the test function.
