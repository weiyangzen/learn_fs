# sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx6.S

Purpose: i.MX6 OCRAM-resident suspend/resume routine for DDR self-refresh, MMDC IO floating/restoration, RBC setup, and physical resume handoff.

Important APIs/types/functions: Defines `imx6_suspend` and macro `resume_mmdc`; consumes `struct imx6_cpu_pm_info` by hard-coded offsets and references `IMX_DDR_TYPE_LPDDR2`.

Control flow: Entry reads pm-info physical/resume/DDR fields, computes physical `resume` label, preloads TLBs, stores resume address and pm-info address in SRC GPRs, syncs L2, forces MMDC self-refresh, writes low-power IOMUXC settings for MMDC pads, masks/restores GPC interrupts around RBC counter enable, executes WFI, and restores MMDC if wake was pending. The `resume` label starts in physical mode, invalidates I-cache, enables I-cache/branch prediction, clears SRC GPRs, restores MMDC from physical bases, and returns to `v7_cpu_resume`.

State and persistence: State lives in the OCRAM pm-info block: physical/virtual bases, saved pad values, DDR type, and resume address. Hardware state spans SRC GPR1/GPR2, MMDC MAPSR/MPDGCTRL0, IOMUXC pad registers, GPC IMR1-4, CCM CCR, and cache controller state.

Dependencies and integration points: Depends on `pm-imx6.c`, `resume-imx6.S`, PL310 definitions, ARMv7 low-level suspend framework, MMDC DDR type from `mmdc.c`, and exact SoC pad offset tables.

Risks: This is one of the highest-risk files in the set. C/assembly layout drift, wrong pad offsets, broken LPDDR2 special handling, or bad physical/virtual base selection can hang resume. Poll loops have no timeout. It must remain physical-address safe after wake.

Test signals: Run mem suspend/resume on every supported i.MX6 variant and DDR type, test wake-pending path, LPDDR2 read-FIFO reset path, and inspect offsets after any C struct change.
