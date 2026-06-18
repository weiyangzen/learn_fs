# sources/distributed-fs/ceph-client/drivers/media/platform/allegro-dvt/Kconfig

## Purpose

This Kconfig file exposes the Allegro DVT Video IP Core encoder driver as `VIDEO_ALLEGRO_DVT`. The help text identifies the hardware as an Allegro DVT encoder IP used in Xilinx ZynqMP EV family devices, called VCU in Xilinx documentation.

## Important APIs, Types, And Symbols

- `VIDEO_ALLEGRO_DVT` is a tristate driver symbol.
- It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, and either `ARCH_ZYNQMP` or `COMPILE_TEST`.
- It selects `V4L2_MEM2MEM_DEV`, `VIDEOBUF2_DMA_CONTIG`, and `REGMAP_MMIO`.
- The module name is documented as `allegro`.

## Control Flow

The symbol is visible only when the top media platform and memory-to-memory dependencies are enabled. If selected as built-in or module, the corresponding Makefile builds `allegro.o`.

## State And Persistence

The only persistent state is the `.config` value for `VIDEO_ALLEGRO_DVT`. At runtime, driver state is implemented in `allegro-core.c`, not here.

## Dependencies And Integration Points

The selected dependencies match the implementation: the driver registers a V4L2 mem2mem video node, uses contiguous DMA buffers through vb2, and maps MCU/SRAM register spaces through regmap MMIO.

## Risks

The dependency on `ARCH_ZYNQMP || COMPILE_TEST` prevents accidental visibility on unrelated platforms, but compile-test builds still need headers for the media and regmap APIs. Missing selected dependencies would cause link or compile failures in the driver body.

## Test Signals

Check Kconfig visibility on ZynqMP defconfigs and allmodconfig. A successful module build should produce `allegro.ko` when the symbol is set to `m`.
