# sources/distributed-fs/ceph-client/arch/s390/kernel/kexec_elf.c

Purpose: loader for ELF kernels passed to the `kexec_file_load` syscall on s390.

Important APIs: `s390_kexec_elf_ops` supplies `.probe`, `.load`, and optional `.verify_sig`. `s390_elf_probe()` only checks ELF magic so invalid ELF-like images are rejected by the stricter loader. `s390_elf_load()` validates executable 64-bit s390 ELF headers, program header bounds, no `PT_INTERP`, and segment sizing. `kexec_file_add_kernel_elf()` adds each `PT_LOAD` segment through `kexec_add_buffer()`.

Control flow and state: loader chooses the entry point from ELF `e_entry` or `STARTUP_KDUMP_OFFSET` for crash kernels, aligns segment memory by `p_align`, offsets crash images by `crashk_res.start`, records the segment containing the entry as `data->kernel_buf`, `kernel_mem`, and `parm`, accumulates `data->memsz`, and adds signed/verified components to the IPL report.

Dependencies and integration: called by `machine_kexec_file.c` through `kexec_file_add_components()`. Depends on generic kexec buffers, ELF helpers, crash dump resource state, and IPL report helpers.

Risks and test signals: segment bound validation and alignment drive memory placement. Test malformed ELF headers, missing/oversized program headers, crash vs normal load, entry-in-segment detection, command line parm area writes, and secure IPL report contents.
