# sources/distributed-fs/ceph-client/samples/fprobe/Makefile

Purpose: builds the fprobe sample module.

Important APIs/functions: maps `CONFIG_SAMPLE_FPROBE` to `fprobe_example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: depends on fprobe/ftrace support selected by Kconfig.

Risks: none beyond sample config correctness.

Test signals: enabling `CONFIG_SAMPLE_FPROBE` should build `fprobe_example.ko`.
