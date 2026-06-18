# sources/distributed-fs/ceph-client/samples/livepatch/Makefile

Purpose: builds livepatch demonstration modules and their support modules.

Important APIs/functions: maps `CONFIG_SAMPLE_LIVEPATCH` to `livepatch-sample.o`, shadow-variable demo modules, and callback demo modules.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: livepatch infrastructure.

Risks: all livepatch samples are selected together and must match target symbol names in their companion modules/kernel.

Test signals: enabling `CONFIG_SAMPLE_LIVEPATCH` builds all listed modules.
