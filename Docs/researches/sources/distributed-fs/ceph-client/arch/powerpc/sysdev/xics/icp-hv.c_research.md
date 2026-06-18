<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-hv.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-hv.c

Purpose: Implements the XICS Interrupt Presentation Controller backend using pSeries hypervisor hcalls.

Important APIs/types/functions: Entry point is `icp_hv_init()`. Backend operations are `icp_hv_get_irq()`, `icp_hv_eoi()`, `icp_hv_set_cpu_priority()`, `icp_hv_teardown_cpu()`, `icp_hv_flush_ipi()`, and SMP `icp_hv_cause_ipi()`/`icp_hv_ipi_action()`. Low-level helpers wrap `H_XIRR`, `H_CPPR`, `H_EOI`, and `H_IPI`.

Control flow: Init checks for an XICP OF node and installs `icp_hv_ops`. Interrupt retrieval calls `H_XIRR` with the current CPPR top, maps the returned vector, pushes CPPR for mapped interrupts, masks and EOIs unknown vectors, and returns zero for spurious. EOI pops CPPR and calls `H_EOI`. IPI send writes MFRR with `H_IPI`; IPI handler clears it to `0xff` and demuxes SMP messages.

State and persistence: Persistent state is the global `icp_ops` pointer and per-CPU XICS CPPR stack maintained by common code. Hypervisor-maintained CPPR/XIRR/MFRR state is mutated through hcalls.

Dependencies and integration points: Depends on pSeries hypervisor calls, XICS common domain/CPPR helpers, OF XICP nodes, SMP IPI demux, and firmware feature selection in `xics_init()`.

Risks: Hcall failures warn but leave the kernel with limited recovery; `icp_hv_set_xirr()` falls back to setting CPPR after bad EOI. Correct CPPR stack pairing between get_irq/retrigger/EOI is critical.

Test signals: LPAR pseries boot, external interrupt delivery, IPI send/clear, CPU teardown/kexec, unknown vector masking, and hcall failure injection if available.

Source read size: 181 lines, 3840 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/xics/icp-hv.c -->
