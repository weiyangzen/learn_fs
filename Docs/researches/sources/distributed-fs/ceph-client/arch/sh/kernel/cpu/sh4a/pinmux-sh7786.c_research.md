# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7786.c

Purpose: registers the SH7786 PFC resource range.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7786`; the resource covers `0xffcc0000-0xffcc008f`.

Control flow: the PFC registration runs as an `arch_initcall`; later SH7786 platform device setup and external interrupt pin setup use the PFC core.

State and persistence: no local mutable state; pin state persists in SoC PFC registers.

Dependencies and integration points: works with SH7786 setup for serial, timers, DMA, USB, SMP interrupt distribution, and optional SCIF1 demuxing.

Risks: SH7786 has many interrupt and peripheral mux paths; PFC range mistakes can break early console or USB/PCIe board wiring.

Test signals: PFC probe success, working serial pins, and successful board-specific pin requests validate this registration.
