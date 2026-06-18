# sources/distributed-fs/ceph-client/drivers/media/platform/st/stm32/stm32-dcmipp/dcmipp-common.h

Purpose: defines the shared constants, entity wrapper, registration helpers, register accessors, colorimetry clamp macro, and entity init/release prototypes for the STM32 DCMIPP driver.

Important types and APIs: constants define the platform driver name, min/max/default frame sizes, and default colorimetry. `dcmipp_colorimetry_clamp` normalizes invalid V4L2 colorimetry fields for both pixel and mbus formats. `struct dcmipp_ent_device` wraps a media entity, pads, input bus description/type, and optional hard/threaded IRQ callbacks with last handler return. `dcmipp_pads_init`, `dcmipp_pads_cleanup`, `dcmipp_ent_sd_register`, and `dcmipp_ent_sd_unregister` form the common entity lifecycle API. `reg_read`, `reg_write`, `reg_set`, and `reg_clear` macros add device-scoped debug logging around relaxed MMIO access. Prototypes expose input, byteproc, and bytecap entity init/release functions.

Control flow and integration: `dcmipp-core.c` builds the topology from the entity init/release prototypes and dispatches shared IRQs using the callback fields. Entity files use the register macros and colorimetry clamp to keep behavior consistent.

State and persistence: the header defines in-memory state only. `dcmipp_ent_device` is the shared runtime handle that lets core traverse subdevices and video nodes uniformly.

Dependencies and risks: depends on Linux IRQ/slab and media/V4L2/fwnode headers. Risks include macro side effects from evaluating `device` multiple times, relaxed MMIO ordering assumptions, broad colorimetry validity thresholds, and the shared entity wrapper needing to work for both subdev and video_device containers. Test signals are compile coverage for all DCMIPP entities, runtime media graph creation, invalid colorimetry TRY/S_FMT tests, and dynamic debug traces of register access.
