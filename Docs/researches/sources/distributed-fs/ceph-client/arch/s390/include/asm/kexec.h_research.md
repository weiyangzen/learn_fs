# sources/distributed-fs/ceph-client/arch/s390/include/asm/kexec.h

Purpose: This header defines s390 kexec and kdump architecture limits, loader state, relocation hooks, IPL-report integration, and crash-kernel protection hooks.

Important APIs/types/functions: It defines memory limits, `KEXEC_ARCH`, `KEXEC_BUF_MEM_UNKNOWN`, dummy `crash_setup_regs()`, `struct s390_load_data`, `s390_verify_sig()`, `kexec_file_add_components()`, `arch_kexec_do_relocs()`, `struct kimage_arch`, image ops declarations, crash-dump protect/unprotect APIs, and kexec_file relocation/cleanup hooks.

Control flow: The kexec_file loader verifies the kernel, loads segments into memory, tracks parmarea and total segment size, builds IPL report components, applies relocations for purgatory or image sections, and prepares firmware-visible IPL data for the next boot.

State and persistence: Persistent state includes `kimage_arch.ipl_buf`, loaded segment memory, parmarea content, IPL report state, and crashkernel reserved memory protection.

Dependencies and integration points: It depends on processor/page/setup definitions, Linux kexec_file_ops, ELF relocation handling, `ipl.h` reports, purgatory, and crash dump configuration.

Risks and test signals: Address limit mistakes can place control pages outside firmware-reachable memory, and relocation errors can make purgatory fail. Tests should cover kexec_file ELF/image load, signature verification, crashkernel reservation/protection, dump kernel boot, and segment-at-zero support.
