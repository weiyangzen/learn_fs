## sources/distributed-fs/ceph-client/arch/s390/net/Makefile

Purpose: declares the s390 architecture-specific networking objects selected by kernel configuration.

Important APIs, types, and functions: build variables add `bpf_jit_comp.o` and `bpf_timed_may_goto.o` when `CONFIG_BPF_JIT` is enabled, and `pnet.o` when `CONFIG_HAVE_PNETID` is enabled.

Control flow: Kbuild conditionally includes objects based on config symbols; there is no runtime control flow.

State and persistence: no runtime state. It controls which object files are linked into the kernel or module build.

Dependencies and integration points: integrates s390 BPF JIT support with core BPF JIT configuration and PNET ID support with network device identification.

Risks: omitting `bpf_timed_may_goto.o` while enabling the JIT would leave the JIT's timed-may-goto support unresolved. Incorrect config guard would compile code on unsupported configurations or miss required helpers.

Test signals: build matrix with `CONFIG_BPF_JIT=y/n` and `CONFIG_HAVE_PNETID=y/n`, plus link checks for `arch_bpf_timed_may_goto` and `pnet_id_by_dev_port`.
