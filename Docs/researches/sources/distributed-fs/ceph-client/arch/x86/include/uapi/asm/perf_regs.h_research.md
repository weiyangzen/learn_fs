<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/perf_regs.h

Purpose: Defines x86 register IDs used by perf sample register masks, including GPR and XMM register numbering.

Important APIs/types/functions: `enum perf_event_x86_regs`, `PERF_REG_X86_32_MAX`, `PERF_REG_X86_64_MAX`, `PERF_REG_X86_XMM*`, `PERF_REG_X86_XMM_MAX`, and `PERF_REG_EXTENDED_MASK`.

Control flow: Perf event setup uses these IDs in user register masks; sampling code maps saved register state to the requested IDs.

State and persistence behavior: No state. Register IDs are a userspace ABI for perf.data and perf_event_open masks.

Dependencies and integration points: Integrates with perf, unwinding, sample decoding, BPF/perf consumers, and extended register sampling.

Risks and test signals: Risks include ID reordering, incorrect 128-bit XMM mask handling, and 32-bit/64-bit register boundary mistakes. Test `perf record --user-regs`, perf.data decoding, XMM sampling, and i386 versus x86_64 masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/perf_regs.h -->
