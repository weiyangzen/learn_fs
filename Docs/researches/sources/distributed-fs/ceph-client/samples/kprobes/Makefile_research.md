# sources/distributed-fs/ceph-client/samples/kprobes/Makefile

Purpose: builds kprobe and kretprobe sample modules.

Important APIs/functions: maps `CONFIG_SAMPLE_KPROBES` to `kprobe_example.o` and `CONFIG_SAMPLE_KRETPROBES` to `kretprobe_example.o`.

Control flow: build-only.

State and persistence: none.

Dependencies and integration: Kprobes/Kretprobes kernel support.

Risks: none in build file.

Test signals: enabling each config compiles its sample module.
