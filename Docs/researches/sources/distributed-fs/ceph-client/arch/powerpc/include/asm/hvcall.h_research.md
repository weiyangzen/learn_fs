# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/hvcall.h

Purpose: Defines the pSeries/PAPR hypervisor call ABI: return codes, flags, opcode numbers, capability bits, hcall wrapper prototypes, and data structures for memory, performance, and nested guest state.

Important APIs, types, and functions: Provides `HVSC`, `H_SUCCESS` and extensive error/long-busy codes, `H_IS_LONG_BUSY()`, page/TCE/VPA/RPTI/guest capability flags, all major `H_*` opcodes through `MAX_HCALL_OPCODE`, `plpar_hcall_norets()`, raw/notrace variants, `plpar_hcall()`, `plpar_hcall9()`, tracepoint hooks, `h_get_mpp()`, `h_get_mpp_x()`, `get_longbusy_msecs()`, `struct hv_guest_state`, and GPCI request structs.

Control flow: Callers select an opcode/flags, invoke a `plpar_hcall*` wrapper, inspect the PAPR return code, optionally retry on long-busy codes using the provided delay hint, and decode retbuf/data structures.

State and persistence: The header holds no state. Hcalls mutate hypervisor-owned partition, memory, interrupt, VIO, KVM guest, and platform state. Tracepoint static-key state is external.

Dependencies and integration points: Integrates pSeries platform code, KVM Book3S HV, VIO, IOMMU/TCE, memory hotplug, secure VM, persistent keys, SCM, XIVE, and performance counter paths.

Risks: Opcode/flag constants are firmware ABI. Return-code sign conventions mix positive busy hints and negative errors. Raw calls are used in real mode and must avoid tracing/statistics. `hv_guest_state_size()` must stay version-compatible as fields are appended.

Test signals: Hcall wrapper ABI tests, long-busy retry handling, tracepoint entry/exit, nested guest state versions 1 and 2, GPCI buffer sizing, and platform firmware tests for representative opcodes.
