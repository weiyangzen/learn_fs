# sources/distributed-fs/ceph-client/arch/arm/mach-imx/resume-imx6.S

Purpose: Physical-address-safe i.MX6 CPU resume trampoline.

Important APIs/types/functions: Defines `v7_cpu_resume`, calls `v7_invalidate_l1`, optional `l2c310_early_resume`, then branches to generic `cpu_resume`.

Control flow: Resume starts from physical context after low-power wake, invalidates L1, restores early PL310 state when configured, and hands back to the ARM suspend framework.

State and persistence: No data state. It mutates CPU cache-controller state during resume.

Dependencies and integration points: Depends on ARMv7 assembler helpers, `cpu_resume`, optional L2X0 support, and the PM code that writes this symbol as the resume address.

Risks: Must remain physical-address safe; absolute data references would fail before MMU restoration. Cache ordering must match the suspend path.

Test signals: Suspend-to-RAM resume on i.MX6 with and without PL310, especially after OCRAM suspend.
