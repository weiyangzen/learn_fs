# sources/distributed-fs/ceph-client/samples/kdb/Makefile

Purpose: builds the KDB hello command sample.

Important APIs/functions: maps `CONFIG_SAMPLE_KDB` to `kdb_hello.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on KDB support.

Risks: none in Makefile.

Test signals: enabling `CONFIG_SAMPLE_KDB` compiles the module.
