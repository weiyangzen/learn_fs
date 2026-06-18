# sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.h

Purpose: Defines shared AXG FIFO constants, register offsets, interrupt bits, the FIFO runtime structure, match-data contract, and exported PCM/probe helper prototypes.

Important APIs and types: `AXG_FIFO_CH_MAX`, `AXG_FIFO_FORMATS`, and `AXG_FIFO_BURST` define generic FIFO PCM capabilities. Register constants cover `FIFO_CTRL0/1/2`, DMA address registers, status registers, and threshold/selector fields. `struct axg_fifo` stores per-device resources. `struct axg_fifo_match_data` lets FRDDR/TODDR drivers provide component driver, DAI driver, and threshold field layout.

Control flow: No executable logic. The header is the internal ABI between `axg-fifo.c` and frontend-specific FIFO drivers.

State and persistence: Declares resource state for one FIFO hardware block and register definitions for persistent FIFO hardware state.

Dependencies and integration points: Included by `axg-fifo.c`, `axg-frddr.c`, and TODDR companion code. Exports are used across separate modules, so prototypes must match symbol exports.

Risks: Changing format masks or channel maxima affects all AXG FIFO frontends. Register-field definitions are reused for multiple SoC variants and must match match-data field positions.

Test signals: Build/link coverage for FRDDR/TODDR modules, compile-time format support in DAI drivers, and runtime FIFO probe using match data.
