# sources/distributed-fs/ceph-client/drivers/video/fbdev/carminefb_regs.h

## Purpose
`carminefb_regs.h` defines Carmine register block offsets, display-layer offsets, bit masks, shifts, and default control values used to program display timing, layers, DRAM control, writeback, graphics interrupts, and clock/reset state.

## Important APIs, Types, and Functions
The header has no functions. Key groups include top-level block bases (`CARMINE_GRAPH_REG`, `CARMINE_DISP0_REG`, `CARMINE_DISP1_REG`, `CARMINE_WB_REG`, `CARMINE_DCTL_REG`, `CARMINE_CTL_REG`), display enable/mode bits (`CARMINE_DEN`, `CARMINE_L0E`, `CARMINE_EXT_CMODE_DIRECT24_RGBA`), timing shifts, layer origin/display/window registers, DCTL state masks, and control register offsets.

## Control Flow
No executable flow exists. `carminefb.c` composes register addresses as `mapped_base + block + offset` and writes values with `writel()`.

## State and Persistence
The constants describe hardware state layout. Values written through these offsets persist in Carmine hardware until reset, power loss, or driver teardown.

## Dependencies and Integration Points
This header is coupled directly to the Carmine register map and the sequences in `init_hardware()`, `carmine_init_display_param()`, and `set_display_parameters()`. It must also align with the display-memory layout in `carminefb.h`.

## Risks and Edge Cases
Register maps are dense and some layer 6/7 offsets live far from layers 0-5, so manual edits can easily introduce address mistakes. Bit shifts and masks need hardware-manual validation before adding modes or overlay support. Incorrect DCTL timing constants can prevent DRAM initialization.

## Test Signals
Compile coverage plus hardware register readback is important. Functional signals include display timing correctness, layer 0 enable, clock/reset behavior, successful DRAM state transition, and no unexpected graphics/VRAM interrupt mask behavior.
