<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h` enumerates arm64 perf register IDs from x0-x30 through SP, PC, PSTATE, and max sentinel values. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_ASM_ARM64_PERF_REGS_H`, `PERF_REG_EXTENDED_MASK`; types: `perf_event_arm_regs`. The file is 48 lines / 1070 bytes. There are no direct C include dependencies in this file.

### Control Flow
perf sample collection and unwinding code use the enum and masks to select which registers are captured or exposed to tooling.

### State, Persistence, And Dependencies
Register samples live in perf event records; this header fixes their numeric ABI. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Renumbering registers breaks perf data interpretation, BPF perf programs, and unwinder tooling.

### Test Signals
Run perf register sampling tests, `perf record --intr-regs`, and BPF stack/register selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/perf_regs.h -->
