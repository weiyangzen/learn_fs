<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.h

## Purpose
Private register and clock definition header for the OMAP DMIC ASoC driver and machine drivers that configure DMIC clocks.

## APIs, Types, and Functions
Defines DMIC register offsets, IRQ/DMA/CTRL/FIFO bit masks, output format constants, FIFO threshold maximum, and `enum omap_dmic_clk` values: PAD_CLKS, SLIMBUS, sync mux, and ABE DMIC output clock. It contains no functions or runtime storage.

## Control Flow, State, and Persistence
This header is compile-time configuration only. Its values are consumed by `omap-dmic.c` for MMIO programming and by `omap-abe-twl6040.c` to request the correct input/output clocks through `snd_soc_dai_set_sysclk()`.

## Dependencies and Integration
Included by OMAP DMIC controller and ABE/TWL6040 machine code. The clock enum is part of the internal machine-driver contract and must match the `set_sysclk` implementation in `omap-dmic.c`.

## Risks and Test Signals
Risks are primarily register-definition drift against hardware manuals, misspelled `OMAP_DMIC_SYSCLK_SLIMBLUS_CLKS`, and callers depending on enum numeric values. Test signals are successful DMIC build, correct bitfields in CTRL/FIFO/DMA registers under capture, and machine-driver clock configuration acceptance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/omap-dmic.h -->
