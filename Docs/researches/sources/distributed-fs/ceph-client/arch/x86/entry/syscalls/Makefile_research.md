## sources/distributed-fs/ceph-client/arch/x86/entry/syscalls/Makefile

Purpose: build rules for generated x86 syscall headers and syscall dispatch tables from `syscall_32.tbl`, `syscall_64.tbl`, and Xen hypercall definitions.

Important targets/APIs: `$(uapi)/unistd_32.h`, `$(uapi)/unistd_x32.h`, `$(uapi)/unistd_64.h`, `$(out)/unistd_32_ia32.h`, `$(out)/unistd_64_x32.h`, `$(out)/syscalls_32.h`, `$(out)/syscalls_64.h`, `$(out)/syscalls_x32.h`, and `$(out)/xen-hypercalls.h`. It wraps `scripts/syscallhdr.sh`, `scripts/syscalltbl.sh`, and `scripts/xen-hypercalls.sh`.

Control flow: variables such as `abis`, `offset`, and `prefix` are target-specific, so the same scripts emit ABI-specific UAPI numbers, prefixed internal declarations, and switch-table include files. `all` builds UAPI and internal headers according to `CONFIG_X86_64`, `CONFIG_X86_X32_ABI`, and `CONFIG_XEN`.

State/persistence: generated files land under `arch/$(SRCARCH)/include/generated/...` and are tracked by Kbuild `targets` for rebuild decisions. The Makefile creates generated include directories with `mkdir -p`.

Integration points: syscall dispatch C files, userspace UAPI, Xen code, Kbuild `if_changed`, and ABI table files.

Risks: wrong ABI filters or offsets can corrupt syscall numbers across native, IA32, and x32 ABIs. Test signals include clean incremental builds, `make headers_install`, syscall table diff checks, x32/IA32 builds, and build reproducibility after `.tbl` edits.
