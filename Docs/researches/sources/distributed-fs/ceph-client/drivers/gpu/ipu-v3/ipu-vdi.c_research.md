# sources/distributed-fs/ceph-client/drivers/gpu/ipu-v3/ipu-vdi.c

## Purpose

`ipu-vdi.c` implements the IPUv3 Video De-Interlacer helper. It programs VDI frame size, chroma format, motion mode, field order, FIFO burst/watermark defaults, module gating, and lookup for capture/display pipelines that need deinterlacing.

## Important APIs, Types, And Functions

`struct ipu_vdi` stores the VDI MMIO base, module enable mask, spinlock, use count, and parent `ipu_soc`. Exported APIs are `ipu_vdi_set_field_order()`, `ipu_vdi_set_motion()`, `ipu_vdi_setup()`, `ipu_vdi_enable()`, `ipu_vdi_disable()`, `ipu_vdi_get()`, and `ipu_vdi_put()`. Internal helpers `ipu_vdi_read()` and `ipu_vdi_write()` wrap register access to `VDI_FSIZE` and `VDI_C`.

## Control Flow

Initialization allocates the VDI object, installs it in `ipu->vdi_priv`, maps a page at the supplied base, records the module bit, and initializes the spinlock. Setup writes `(yres - 1, xres - 1)` into `VDI_FSIZE`, derives 4:2:2 versus 4:2:0 mode from the media bus code, and applies burst and watermark defaults. Field-order and motion setters update only their fields. Enable/disable gate the IPU module around a reference count.

## State And Persistence Behavior

Persistent software state is the devm-managed `ipu_vdi` object and its `use_count`. `ipu_vdi_get()` simply returns the singleton; `ipu_vdi_put()` is a no-op. Hardware state in `VDI_C` and `VDI_FSIZE` persists across users until explicitly changed or reset.

## Dependencies And Integration Points

It depends on Linux MMIO/spinlocks, V4L2 field and standard constants, media bus format constants from public IPU headers, and `ipu_module_enable()/disable()`. It integrates with deinterlacing paths that configure VDI before feeding the IC or display/capture flow.

## Risks And Test Signals

Risks include singleton access with no ownership tracking, no validation for zero or overflowing dimensions, `VDI_C` setup using OR without clearing prior chroma/burst bits, field-order fallback based on `V4L2_STD_525_60`, and no explicit teardown. Test with 4:2:2 and 4:2:0 inputs, all V4L2 field orders, low/medium/high motion settings, repeated setup changes, enable/disable nesting, and deinterlaced capture output validation.
