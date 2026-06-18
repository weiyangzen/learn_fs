<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/head.S -->
# sources/distributed-fs/ceph-client/arch/s390/purgatory/head.S

Purpose: This assembly file is the s390 purgatory entry and transition code that verifies the next kernel image, optionally returns to the old kernel for crash-check-only mode, swaps crash memory into address zero, and starts the next kernel with `diag 0x308`.

Important APIs/types/functions: The main exported code symbol is `purgatory_start`. Macros include `MEMCPY`, `MEMSWAP`, and `START_NEXT_KERNEL`. The code references purgatory data symbols such as `kernel_entry`, `load_psw_mask`, `kernel_type`, `crash_start`, `crash_size`, `purgatory_sha_regions`, `purgatory_end`, `stack`, `gprregs`, and `disabled_wait_psw`, and calls `verify_sha256_digest`.

Control flow: Entry sets architecture/addressing mode, saves registers, sets up a stack, and determines whether a crash kernel invocation is checksum-only. It calls SHA-256 verification; checksum-only returns to the old kernel, mismatch loads a disabled wait PSW, normal kexec starts the next kernel directly, and crash kexec relocates purgatory to the end of the target crash-memory destination before swapping memory ranges and starting the crash kernel. The crash path iterates over SHA regions to avoid overwriting active purgatory data during the swap.

State and persistence: It mutates CPU registers, stack/buffer memory, crash-memory contents, PSW state, and the lowcore/kernel entry handoff. Saved GPRs allow checksum-only crash invocations to return. After the point of no return, it uses its own stack area as a temporary copy buffer.

Dependencies and integration points: It depends on s390 assembly ABI, page alignment, SIGP architecture setup, kexec SHA region layout, purgatory C verification code, and the s390 restart `diag 0x308` interface. It is linked by `purgatory.lds.S` and embedded by `kexec-purgatory.S`.

Risks and test signals: Register conventions and self-relocation math are fragile; an off-by-one in crash-memory swapping can corrupt purgatory or the crash kernel. Checksum-only mode must restore registers and return safely. Tests include normal kexec, kdump checksum-only failure/success, crash kernel boot with varied crash memory sizes/segment layouts, and disassembly review of relocation-independent code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/purgatory/head.S -->
