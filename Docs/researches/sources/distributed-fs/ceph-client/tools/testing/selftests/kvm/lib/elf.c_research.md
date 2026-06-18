# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/elf.c

## Purpose
This utility loads the current selftest ELF image into a guest VM's virtual address space, allowing guest code and data from the test binary to run inside KVM.

## Important APIs, Types, and Functions
`elfhdr_get()` opens and validates a 64-bit ELF header, including magic, class, host-matching endianness, version, and program/section header sizes. `kvm_vm_elf_load()` walks program headers, allocates guest virtual memory for each `PT_LOAD` segment, zeroes BSS, and copies file-backed bytes.

## Control Flow
The loader opens the file, validates the header, iterates all program headers, skips non-loadable entries, aligns segment virtual ranges to guest pages, allocates exactly at the segment's requested GVA, clears memory, seeks to segment data, and reads bytes into the guest mapping.

## State, Dependencies, and Integration
State is transient file descriptor and allocated guest pages. It depends on `test_read()`, `__vm_alloc()`, `addr_gva2hva()`, ELF UAPI definitions, and `kvm_util.c` VM creation. `__vm_create()` loads `program_invocation_name` through this path.

## Risks and Test Signals
The loader supports only ELF64 with same-endian host and guest file representation and does not enforce segment permissions. Failures are assertion messages for malformed ELF, allocation mismatch, short reads, or seek errors.
