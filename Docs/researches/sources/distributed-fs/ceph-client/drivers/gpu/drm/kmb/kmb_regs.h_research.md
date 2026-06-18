<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_regs.h

## Purpose
Provides register offsets, bit fields, and convenience macros for the Keem Bay LCD controller, layer DMA/CSC/format registers, MIPI DSI transmitter, D-PHY, IRQ blocks, MSSCAM syscon routing, and QoS-related registers.

## Important APIs, types, and functions
Important groups include LCD control and interrupt bits, layer configuration and DMA address macros `LCD_LAYERn_*`, output timing and format registers, MIPI HS controller register macros `MIPI_TXm_*`, FIFO allocation helpers `SET_MC_FIFO_*`, MIPI IRQ masks, D-PHY test/control/status macros, PLL lock and stop-state helpers, and MSSCAM route/clock/reset constants.

## Control flow
The file is declarative, but some macros expand to MMIO helper calls. Address macros compute per-layer and per-MIPI-controller offsets used in plane, CRTC, IRQ, and DSI programming.

## State and persistence
No C state is stored. The definitions describe hardware state programmed by the KMB driver: LCD enable/interrupt/layer/DMA/timing, output format, MIPI controller configuration, D-PHY lane and PLL state, and syscon route/reset bits.

## Dependencies and integration points
Consumed by all KMB C files. Macro call helpers assume `kmb_write_bits_mipi()`, `kmb_read_mipi()`, and related functions are in scope.

## Risks
Register arithmetic and bit positions are central to hardware correctness. There is a duplicate `DPHY_INIT_CTRL2` definition, and macros with side effects can obscure call sites. Wrong layer stride offsets or FIFO masks can corrupt display DMA. D-PHY macros use DPHY numbering assumptions around 6 and 7.

## Test signals
Compile-time use catches some symbol drift. Runtime validation is successful modeset, correct scanout colors, stable DMA, MIPI link bring-up, D-PHY lock, and expected interrupt status/clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/kmb/kmb_regs.h -->
