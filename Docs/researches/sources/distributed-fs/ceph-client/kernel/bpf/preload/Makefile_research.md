# sources/distributed-fs/ceph-client/kernel/bpf/preload/Makefile

Purpose: builds the `bpf_preload` kernel module and points its CFLAGS at the in-tree libbpf headers needed by generated lightweight skeleton code. The source was read as a complete 7-line file.

Important APIs/rules: `LIBBPF_INCLUDE = $(srctree)/tools/lib`, `obj-$(CONFIG_BPF_PRELOAD_UMD) += bpf_preload.o`, `CFLAGS_bpf_preload_kern.o += -I$(LIBBPF_INCLUDE)`, and `bpf_preload-objs += bpf_preload_kern.o`.

Control flow: no runtime flow. Kbuild compiles `bpf_preload_kern.o` into the module when `CONFIG_BPF_PRELOAD_UMD` is enabled.

State and persistence: build metadata only.

Dependencies/integration: integrates with Kbuild, the preload Kconfig, and generated skeleton headers that include libbpf internal skeleton support.

Risks and edge cases: include path drift in `tools/lib` or skeleton API changes can break module builds. The module has a single object, so generated header changes fully rebuild it.

Test signals: kernel module build with `CONFIG_BPF_PRELOAD_UMD=m/y`, include path validation, and modpost/module load checks.
