# sources/distributed-fs/ceph-client/include/linux/mfd/wcd934x/wcd934x.h

## Purpose
`wcd934x/wcd934x.h` declares the minimal parent-device state for Qualcomm WCD934x MFD/audio codec support. It connects regmap, device identity, GPIO descriptors, and IRQ bookkeeping to codec child drivers.

## Important APIs, Types, and Functions
`struct wcd934x_ddata` contains the parent `device`, Slimbus device pointer, regmap, reset GPIO descriptor, master-bias GPIO descriptor, device ID, per-IRQ-type counters, and regmap IRQ chip data. There are no function prototypes or register constants in this file; those live in `registers.h`.

## Control Flow
The parent driver creates/populates `wcd934x_ddata`, controls reset and master-bias GPIOs during probe and power sequencing, initializes regmap and IRQ data, and supplies this state to codec/child drivers. IRQ type counters allow software to track interrupt configuration/use per logical type.

## State and Persistence Behavior
Software state includes regmap, reset/mbias GPIO ownership, hardware device ID, IRQ counters, and IRQ chip data for the device lifetime. Hardware state controlled through this struct includes reset line and master-bias enable line; detailed codec register state is external to this header.

## Dependencies and Integration Points
The header depends on Slimbus, GPIO descriptor, IRQ, and regmap APIs. It integrates with Qualcomm WCD934x Slimbus probing, regmap, regmap-irq, reset/bias GPIO handling, and ASoC codec subdrivers.

## Risks and Test Signals
Risks include missing GPIO descriptors on boards that require explicit reset/bias, mismatched device ID with register map assumptions, IRQ count underflow/overflow if not paired, and lifetime issues between Slimbus parent and codec children. Test signals are probe/remove tests with optional GPIOs, reset/bias sequencing tests, device ID readback, IRQ registration/unregistration balance, and codec child probe using populated parent data.
