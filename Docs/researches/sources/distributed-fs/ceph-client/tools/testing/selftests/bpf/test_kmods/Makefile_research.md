# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/test_kmods/Makefile

## Research

This Makefile builds the kernel modules used by BPF selftests. It is a thin wrapper around the kernel build system and selects module objects for `bpf_testmod`, rqspinlock, module-order tests, and no-CFI struct_ops validation.

The important variables are `TESTMODS_DIR`, `KDIR`, and `VMLINUX_BTF`. `obj-m` lists the module targets. `bpf_testmod-objs` composes `bpf_testmod.o` with generated trace event support, while other module targets are single-object modules. The default `all` target invokes `$(MAKE) -C $(KDIR) M=$(TESTMODS_DIR) modules`, optionally passing `KBUILD_EXTRA_SYMBOLS` to resolve exported symbols from the main selftests build. `clean` delegates to the kernel build system clean target.

Control flow and state are make-driven. It creates kernel module build artifacts such as `.ko`, `.o`, `.mod`, generated module metadata, and potentially BTF-enabled module output when `VMLINUX_BTF` is available. Dependencies include a configured kernel build tree, module build support, compiler/toolchain compatibility, and any symbols exported by the broader selftest build.

Risks are mostly build-environment coupling: wrong `KDIR`, stale generated files, missing vmlinux BTF, unavailable architecture features, or unresolved symbols. Test signals are successful `make modules` output and loadable `.ko` files consumed by `test_kmod.sh`, ftrace tests, split-BTF tests, and rqspinlock tests.
