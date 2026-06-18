<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raspberrypi-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/raspberrypi-ts.c

## Purpose
`raspberrypi-ts.c` is a small platform input driver for the Raspberry Pi firmware-backed touchscreen interface. Instead of talking to a touchscreen controller over I2C/SPI, it allocates one coherent DMA page, passes the physical address to the VideoCore firmware with `RPI_FIRMWARE_FRAMEBUFFER_SET_TOUCHBUF`, and polls the firmware-maintained memory layout as a multitouch device.

## Important APIs, Types, And Functions
The main state is `struct rpi_ts`, which stores the platform device, input device, parsed `touchscreen_properties`, the coherent firmware register buffer, and a `known_ids` bitmask. `struct rpi_ts_regs` mirrors the firmware buffer: mode, gesture, number of points, and up to ten packed `rpi_ts_touch` entries. `rpi_ts_probe()` obtains the parent firmware node, calls `devm_rpi_firmware_get()`, allocates DMA memory, registers `rpi_ts_dma_cleanup()` with devres, configures the input axes, initializes ten `INPUT_MT_DIRECT` slots, installs `input_setup_polling()`, and registers the input device. `rpi_ts_poll()` is the runtime data path.

## Control Flow
Probe binds to `raspberrypi,firmware-ts`, registers the DMA buffer with firmware, then exposes a polled `BUS_HOST` input device. Each poll copies `struct rpi_ts_regs` from I/O memory, invalidates `num_points` by writing `99`, and ignores stale or empty data. It decodes X/Y, touch ID, and event type, reports active slots for down/contact events, computes releases from `known_ids & ~modified_ids`, syncs the MT frame, and stores the current active bitmask.

## State And Persistence
Driver state is volatile and devres-managed. The only persistent hardware-visible state is the DMA buffer address registered with firmware during probe; touch slot state is tracked in memory through `known_ids`. There is no firmware upload, sysfs state, suspend path, or file-backed persistence.

## Dependencies And Integration Points
The driver integrates with OF platform matching, Raspberry Pi firmware property calls, coherent DMA APIs, input polling, multitouch slot helpers, and touchscreen DT properties for axis transforms. Firmware must understand the shared-buffer ABI.

## Risks
The firmware buffer address is truncated to `u32`, so it assumes firmware-addressable DMA memory. Data validity depends on the `num_points` invalidation convention. Only down/contact events report coordinates; other event types are ignored. Because it is polled at 17 ms, latency and missed transient states are bounded by polling cadence.

## Test Signals
Useful validation includes successful probe without `Failed to set touchbuf`, `/proc/bus/input/devices` showing `raspberrypi-ts`, evtest/libinput reporting stable ten-slot MT events, DT axis inversion/swap behavior, and release events when fingers leave the panel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raspberrypi-ts.c -->
