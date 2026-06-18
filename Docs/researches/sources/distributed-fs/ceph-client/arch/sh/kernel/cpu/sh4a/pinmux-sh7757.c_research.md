# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4a/pinmux-sh7757.c

Purpose: registers the SH7757 B0-step pinmux resource with the PFC subsystem.

Important APIs, types, and functions: `plat_pinmux_setup()` registers `pfc-sh7757`; `sh7757_pfc_resources` maps `0xffec0000-0xffec008f`.

Control flow: boot-time `arch_initcall` registers the range before SH7757 devices such as SCIF, SPI, DMA, USB, and external IRQ modes need pin functions.

State and persistence: no local runtime state. PFC hardware and the PFC core own pin state after registration.

Dependencies and integration points: integrates with `<cpu/pfc.h>` and SH7757 setup code with multiple DMA engines and external interrupt-pin modes.

Risks: the comment identifies the B0 step; other silicon revisions may have incompatible pin registers. The file has no silicon-step check.

Test signals: `pfc-sh7757` should probe; SPI/SCIF/USB board pin requests should succeed; external IRQ mode selection should be reflected in PFC/GPIO behavior.
