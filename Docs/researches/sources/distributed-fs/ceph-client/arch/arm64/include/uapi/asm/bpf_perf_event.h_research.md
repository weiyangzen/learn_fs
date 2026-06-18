<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h` exposes the arm64 perf-event register type to BPF programs by including the UAPI ptrace register definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_BPF_PERF_EVENT_H__`; types: `user_pt_regs`. The file is 9 lines / 257 bytes. Direct includes are `asm/ptrace.h`.

### Control Flow
BPF/perf tooling includes this header to interpret sampled register state.

### State, Persistence, And Dependencies
No local state; state is the perf sample context supplied to BPF programs. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect register type exposure can break BPF stack/register inspection on arm64.

### Test Signals
Run BPF perf-event selftests and compile libbpf programs that read `struct pt_regs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bpf_perf_event.h -->
