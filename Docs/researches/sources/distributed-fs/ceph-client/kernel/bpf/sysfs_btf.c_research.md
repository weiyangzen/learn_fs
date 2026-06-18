# sources/distributed-fs/ceph-client/kernel/bpf/sysfs_btf.c

## Purpose

`sysfs_btf.c` exposes the built-in kernel BTF blob as `/sys/kernel/btf/vmlinux`. This gives user-space BPF tooling a stable way to read or mmap the kernel's BTF metadata for CO-RE relocation, introspection, and verifier-facing type discovery.

## Important APIs, Types, And Functions

- Linker symbols `__start_BTF` and `__stop_BTF` delimit the vmlinux BTF section generated during kernel link.
- `bin_attr_btf_vmlinux` is a read-only sysfs binary attribute named `vmlinux`.
- `btf_sysfs_vmlinux_mmap()` validates mmap requests and maps the physical pages backing the BTF blob with `remap_pfn_range()`.
- `btf_kobj` is the exported `struct kobject *` for `/sys/kernel/btf`.
- `btf_vmlinux_init()` sets the binary attribute private pointer and size, creates the `btf` kobject under `kernel_kobj`, and registers the binary file at `subsys_initcall` time.

## Control Flow

Initialization computes `size = __stop_BTF - __start_BTF`. If the BTF section is empty, it returns successfully without creating sysfs state. Otherwise it creates `/sys/kernel/btf` and registers `vmlinux` with `sysfs_create_bin_file()`. Reads use `sysfs_bin_attr_simple_read`.

The mmap path only accepts requests against the original BTF start pointer, offset zero, non-writable, non-executable, non-`VM_MAYSHARE` VMAs, and sizes no larger than the page-aligned BTF region. It marks the VMA `VM_DONTDUMP`, strips may-write/may-exec, and remaps the BTF physical PFNs read-only.

## State And Persistence Behavior

The BTF bytes are static kernel image data. The sysfs kobject and binary attribute persist after init for the lifetime of the kernel. No dynamic allocation beyond the kobject registration is maintained by this file.

## Dependencies And Integration Points

The file depends on linker-provided BTF section symbols, sysfs/kobject infrastructure, memory-management helpers, and the BTF build pipeline described by `scripts/link-vmlinux.sh`. It complements `syscall.c` BTF FD and info APIs by exposing the vmlinux BTF blob directly through sysfs.

## Risks And Edge Cases

The mmap path is intentionally strict. Incorrect page alignment of `__start_BTF`, integer wrap in `pfn + pages`, nonzero offsets, or overly large mappings return errors. Permission checks prevent writable or executable mappings of kernel metadata. If the BTF section is absent, tooling must handle the missing sysfs file.

## Test Signals

Useful checks include booting with BTF enabled and verifying `/sys/kernel/btf/vmlinux` exists and is non-empty, comparing file size to the BTF section size, reading the blob with bpftool/libbpf, mmaping read-only offset-zero ranges, and verifying writable/executable/nonzero-offset/oversized mmap attempts fail.
