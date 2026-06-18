<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/perf_regs.h

Source read size: 63 lines, 1427 bytes.

Purpose: enumerates PA-RISC registers exposed through perf sample register masks. Important API: `enum perf_event_parisc_regs` covering general registers, space registers, IAOQ/IASQ, SAR, IIR, ISR, IOR, IPSW, and `PERF_REG_PARISC_MAX`. Control flow: perf core and `perf_regs.c` map enum indices to `pt_regs` fields when collecting samples. State and persistence: sample register state is transient per perf event sample. Dependencies and integration points: must match `struct user_regs_struct` and PA-RISC perf implementation. Risks: enum reordering breaks perf userspace decoding. Test signals: `perf record` with register sampling, DWARF/unwind correlation, and userspace perf header decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/uapi/asm/perf_regs.h -->
