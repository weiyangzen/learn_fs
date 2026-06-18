# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/atmel-isc.h

## Purpose
This header defines the shared data model for the deprecated Atmel/Microchip ISC drivers. It describes ISC clocks, vb2 buffers, async sensor entities, media-bus formats, internal output configuration, histogram/AWB controls, register offsets, the main `isc_device`, callback hooks, and exported common APIs.

## Important APIs and Types
Key types are `struct isc_clk`, `struct isc_buffer`, `struct isc_subdev_entity`, `struct isc_format`, `struct fmt_config`, `struct isc_ctrls`, `struct isc_reg_offsets`, and `struct isc_device`. Pipeline bit constants describe enabled image-processing blocks from DPC through SUB420. Histogram constants define 512 entries and Bayer channels.

`struct isc_device` is the shared runtime object. It stores regmap, clocks, runtime device pointers, V4L2/video objects, vb2 queue state, DMA queue and current frame, active/try formats, controls, work and locks, regmap pipeline fields, async subdevice list/current subdevice, gamma tables, max dimensions, SoC callback functions, register offsets, and supported format lists.

Exported declarations include `atmel_isc_regmap_config`, `atmel_isc_async_ops`, `atmel_isc_interrupt()`, `atmel_isc_pipeline_init()`, `atmel_isc_clk_init()`, `atmel_isc_subdev_cleanup()`, and `atmel_isc_clk_cleanup()`.

## Control Flow and State
The header has no executable flow, but it defines the state passed between SoC probes and the common base. SoC-specific files allocate and fill `isc_device`; the common base mutates it during async bind, format negotiation, streaming, IRQ handling, AWB work, and cleanup. Clock state uses per-clock spinlocks and cached parent/divider values. DMA state uses a spinlocked queue and completion for streamoff.

## Dependencies and Integration Points
It depends on the common clock framework, platform devices, V4L2 controls/device, and vb2 DMA-contig. It is the primary integration point between the SAMA5D2/SAMA7G5 platform files and `atmel-isc-base.c`/`atmel-isc-clk.c`.

## Risks and Test Signals
Risks include struct layout coupling across modules, callback pointers left unset by SoC probe, missing lock usage around mutable fields, and stale comments such as `bpp` being described as bytes while code treats it as bits per pixel. Test signals are compile/link coverage of all exported symbols, probe paths filling every callback/offset, streaming across formats, AWB controls, and KASAN/lockdep during streamon/off and async unbind.
