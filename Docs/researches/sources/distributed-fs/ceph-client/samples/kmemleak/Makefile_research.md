# sources/distributed-fs/ceph-client/samples/kmemleak/Makefile

Purpose: builds the kmemleak test sample.

Important APIs/functions: maps `CONFIG_SAMPLE_KMEMLEAK` to `kmemleak-test.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on kmemleak sample config.

Risks: none in Makefile; runtime intentionally creates leaks.

Test signals: enabling the config builds `kmemleak-test.ko`.
