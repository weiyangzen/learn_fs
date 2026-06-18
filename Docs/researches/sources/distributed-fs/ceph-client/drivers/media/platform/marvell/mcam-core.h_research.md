# sources/distributed-fs/ceph-client/drivers/media/platform/marvell/mcam-core.h

## Purpose
This header defines the shared Marvell camera core contract, including platform-populated device state, buffer mode choices, exported core functions, register I/O helpers, and the CCIC register map used by Cafe and MMP wrappers plus `mcam-core.c`.

## Important APIs, Types, And Constants
Key enums are `enum mcam_state`, `enum mcam_buffer_mode`, and `enum mcam_chip_id`. `struct mcam_frame_state` tracks frames, single-buffer cases, and delivered frames. `struct mcam_camera` is the central device object: platform fields include register base/size, spinlock, device, chip ID, buffer mode, clock/MIPI settings, clock handles, and platform callbacks; private core fields include V4L2 objects, state flags, notifier/sensor, vb2 queue/list, DMA buffers, sequence counters, mode-specific callbacks, current pixel format, media-bus code, and mutex.

The exported functions are `mccic_register()`, `mccic_irq()`, `mccic_shutdown()`, `mccic_suspend()`, and `mccic_resume()`. Inline helpers `mcam_reg_write()`, `mcam_reg_read()`, `mcam_reg_write_mask()`, `mcam_reg_clear_bit()`, and `mcam_reg_set_bit()` centralize MMIO access.

## Control Flow And State
The header does not run code beyond inline register helpers. It describes runtime state ownership: platform code fills the top part of `struct mcam_camera` before calling `mccic_register()`, while the core owns the lower private fields after registration. Register definitions cover DMA BARs, MIPI CSI2 controls, image pitch/size/offset, IRQ status/mask/clear, controller format/control bits, clock control, Cafe upper address, and Armada descriptor registers.

## Dependencies And Integration Points
The header depends on Linux list/clock/workqueue and V4L2/vb2 headers. It is shared by `mcam-core.c`, `cafe-driver.c`, and `mmp-driver.c`. Its compile-time buffer mode macros mirror selected vb2 backends and hard-fail if no supported backend is configured.

## Risks
Because `struct mcam_camera` mixes platform-owned and core-private fields, platform drivers can accidentally modify core state if boundaries are not respected. Register helper callers must hold `dev_lock` when required by the comments. Buffer-mode availability is compile-time conditional, so code paths referenced by platform defaults must be present in Kconfig selections. Register defines are used for multiple chip generations; bits marked Cafe-only or Armada-only should not be applied blindly across variants.

## Test Signals
Compile both Cafe and MMP drivers with each selected backend. Static checks should catch missing vb2 mode symbols. Runtime register dump/debug tests should verify offsets and bit fields for each chip. API tests should ensure platform wrappers initialize all required public fields before `mccic_register()`.
