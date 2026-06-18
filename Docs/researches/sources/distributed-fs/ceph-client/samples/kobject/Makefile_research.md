# sources/distributed-fs/ceph-client/samples/kobject/Makefile

Purpose: builds kobject and kset sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_KOBJECT` to `kobject-example.o` and `kset-example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: kobject/sysfs support.

Risks: both examples are built together when selected.

Test signals: enabling `CONFIG_SAMPLE_KOBJECT` compiles both modules.
