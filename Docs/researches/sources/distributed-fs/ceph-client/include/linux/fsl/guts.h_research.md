# sources/distributed-fs/ceph-client/include/linux/fsl/guts.h

Purpose: maps Freescale/NXP Global Utilities (GUTS) and Run Control/Power Management (RCPM) register layouts and bit definitions for PowerPC/QorIQ SoCs.

Important APIs and types: `struct ccsr_guts` maps POR status, GPIO, mux control, device disable, power management, reset, version, RCW, I/O delay, PAMU bypass, clock, DMA, local bus, DDR clock, SerDes, and transaction control registers. PPC86xx-specific helpers `guts_set_dmacr()` and `guts_set_pmuxcr_dma()` update DMA source/mux bits, with many PMUX/clock divider constants. `struct ccsr_rcpm_v1` and `struct ccsr_rcpm_v2` map low-power, interrupt mask, timebase, power-gating, and deep-sleep registers for different RCPM generations.

Control flow: platform and driver code maps GUTS/RCPM registers, reads boot/configuration state, selects pinmux/DMA routing, gates devices/clocks, controls sleep states, and configures timebase behavior. Inline helpers use big-endian clear/set operations for register fields.

State and persistence: state is SoC-global runtime register programming and boot status. Values may survive until reset and affect many devices, but the header owns no in-memory state.

Dependencies and integration points: depends on I/O accessors and Linux types; integrates with PowerPC platform setup, DMA, audio/SSI, display clocking, low-power suspend, reset, and device-disable code.

Risks and test signals: risks include accessing registers absent on a given chip, endian mistakes, global side effects from mux/clock changes, and incorrect RCPM generation layout. Tests should cover SoC-specific register presence, DMA mux setup, low-power entry/exit, reset-status decoding, clock divider programming, and compile coverage for PPC86xx and non-PPC86xx configs.
