# sources/distributed-fs/ceph-client/security/bpf/Makefile

Purpose: builds the BPF LSM support object when `CONFIG_BPF_LSM` is enabled.

Important APIs, types, and functions: the only build rule is `obj-$(CONFIG_BPF_LSM) := hooks.o`.

Control flow: Kbuild includes `hooks.o` in the security/bpf object list conditionally on the config symbol.

State and persistence: no runtime state.

Dependencies and integration: depends on the kernel Kbuild system and the BPF LSM Kconfig symbol. It directly controls whether `hooks.c` participates in the build.

Risks and test signals: risk is limited to build inclusion. Test signals are successful builds with `CONFIG_BPF_LSM=y/m` and absence of BPF LSM hooks when disabled.
