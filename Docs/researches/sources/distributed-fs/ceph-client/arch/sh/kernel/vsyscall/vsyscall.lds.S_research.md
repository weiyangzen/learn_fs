# sources/distributed-fs/ceph-client/arch/sh/kernel/vsyscall/vsyscall.lds.S

Purpose: linker script for the SH vDSO shared object.

Important symbols and sections: `ENTRY(__kernel_vsyscall)`, `VERSION` exports for `LINUX_2.6`, `.hash`, `.dynsym`, `.dynstr`, `.gnu.version*`, `.text`, `.note`, `.eh_frame_hdr`, `.eh_frame`, `.dynamic`, and discard rules.

Control flow: directs the vDSO link so only intended ABI symbols are globally visible and all sections are laid out from address zero for later page embedding.

State and persistence: build-time ELF layout becomes the runtime vDSO image copied into each process mapping.

Dependencies and integration: depends on generated assembly objects, `asm/asm-offsets.h`, Kbuild linker flags, and user-space dynamic loader/debugger expectations.

Risks: accidental symbol exports or discarded metadata can break libc lookup, signal unwinding, or ELF validation.

Test signals: `readelf -Ws/-S` on `vsyscall.so`, symbol-version checks, and userspace resolving `__kernel_vsyscall`.
