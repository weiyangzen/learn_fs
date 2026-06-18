# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_class.h

## Purpose
Private state definition shared by the SDCA SoundWire class driver and auxiliary class function driver.

## APIs, Types, and Functions
Defines `struct sdca_class_drv` with device pointer, device regmap, SoundWire slave pointer, parsed function-data array, interrupt info, regmap lock, serialized initialization lock, boot work, device-attach completion, and attached flag.

## Control Flow, State, and Persistence
The header has no executable flow. It defines persistent state spanning probe, asynchronous boot, function driver probes, IRQ processing, runtime PM, and suspend/resume. `regmap_lock` serializes device/function regmap access and `init_lock` serializes function initialization/resume/FDL paths.

## Dependencies and Integration
Includes completion, mutex, and workqueue declarations, and forward-declares SDCA, regmap, device, and SoundWire structures. It is included by `sdca_class.c` and `sdca_class_function.c`.

## Risks and Test Signals
Risks are lock-order mistakes between shared regmap and init locks, stale function pointers if auxiliary devices outlive core teardown, and state drift between class and function drivers. Build coverage and runtime probe/remove with multiple functions are the primary signals.
