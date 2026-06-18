# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.h

Purpose: internal ID header for the H616 CCU provider. It augments public H616 binding IDs with private PLL/root IDs used in the driver’s onecell array.

Important APIs, types, and functions: includes `dt-bindings/clock/sun50i-h616-ccu.h` and reset bindings, defines IDs for oscillator, CPUX, DDR0/DDR1, peripheral, GPU, video, VE, DE, audio-HS/audio fixed factors, CPU/bus roots, MBUS, DRAM, bus DRAM, and `CLK_NUMBER`.

Control flow: no runtime execution; macros are consumed by `ccu-sun50i-h616.c`.

State and persistence: no state. Values are array indexes and are therefore correctness-sensitive.

Dependencies and integration points: coordinates the C driver with DT-exposed clock/reset IDs. Comments document which clocks are exported for PRCM, DVFS, PIO, and module use.

Risks and test signals: incorrect numbering can silently wire consumers to wrong clocks. Test via build, boot-time DT clock lookup, `clk_summary` name/rate inspection, and driver probes for CPU, MMC, USB, display, GPU, and audio consumers.
