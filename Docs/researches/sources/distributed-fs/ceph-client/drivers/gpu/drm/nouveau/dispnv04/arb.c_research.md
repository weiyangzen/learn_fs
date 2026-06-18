# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/arb.c

## Purpose
`arb.c` calculates legacy NVIDIA display FIFO arbitration parameters. These “magic” burst and low-watermark values prevent display snow or underrun when framebuffer memory is accessed during scanout.

## Important APIs, Types, And Functions
Internal data structures are `struct nv_fifo_info` (`lwm`, `burst`) and `struct nv_sim_state` with pixel/memory/core clocks, bpp, memory type/width/latency/page miss, and two-head state. `nv04_calc_arb()` handles TNT/NV04-style hardware. `nv10_calc_arb()` handles NV10/NV1x-style FIFO sizing and latency. `nv04_update_arb()` gathers clocks and memory parameters from hardware registers and PCI nForce config. `nv20_update_arb()` supplies fixed parameters for later Kelvin-class hardware. Public `nouveau_calc_arb()` chooses the path based on GPU family and chipset.

## Control Flow, State, And Integration
CRTC code calls `nouveau_calc_arb()` during scanout base programming. The function reads current memory/core clocks and memory configuration, computes burst/lwm, and returns encoded values that `crtc.c` writes to VGA extended CRTC registers. No persistent state is stored; outputs are recomputed from current clocks, bpp, and mode pixel clock.

## Risks And Test Signals
The formulas are empirical and hardware-specific. Division by small clock values, bad memory-width detection, dual-head accounting, and chipset exceptions can all produce underruns. The C51/C512 special case returns values in a different-looking scale than the encoded `ilog2` path and must match hardware expectations. Test signals are visual scanout stability under memory pressure, no snow/tearing on NV04-NV2x, dual-head tests, mode switches across bpp/pixel clocks, and register traces matching historical known-good values.
