## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_reg.h

Purpose: centralizes GuC and HuC MMIO register offsets, status bitfields, DMA controls, scratch registers, shim controls, interrupts, TLB invalidation controls, doorbells, and a packed doorbell cacheline format.

Important APIs, types, and functions:
- Status and scratch definitions: `GUC_STATUS`, `GS_*` masks/shifts, `GUC_HEADER_INFO`, `SOFT_SCRATCH()`, `GEN11_SOFT_SCRATCH()`, `MEDIA_SOFT_SCRATCH()`, and scratch counts.
- RSA/DMA/load definitions: `UOS_RSA_SCRATCH()`, DMA address/copy/control registers, `UOS_MOVE`, `START_DMA`, `DMA_GUC_WOPCM_OFFSET`, WOPCM size/lock fields, HuC status/load info.
- PM/shim/interrupt definitions: GT PM config doorbell enable bits, `GUC_ARAT_C6DIS`, `GUC_SHIM_CONTROL`, `GUC_SHIM_CONTROL2`, `GUC_SEND_INTERRUPT`, host interrupt registers, semaphore interrupt enables, and TLB invalidation controls.
- Doorbell and interrupt definitions include `struct guc_doorbell_info`, Gen8 doorbell registers, Gen12 distributed doorbell population fields, GuC interrupt enable registers, and GuC interrupt vector bits such as `GUC_INTR_GUC2HOST`, DMA done, fatal error, notification error, and software interrupts.

Control flow:
- Register constants are consumed by firmware upload, notification, interrupt, TLB invalidation, HuC load, and GuC runtime setup code.

State and persistence:
- This header defines hardware state addresses and bit meanings, not driver-owned state.

Dependencies and integration points:
- Includes `i915_reg_defs.h` for `_MMIO()` and kernel integer/compiler headers.
- Shared by GuC firmware loading, CT notification, power-management setup, and GuC/HuC authentication flows.

Risks:
- Incorrect offsets or masks can break firmware loading, status decoding, interrupts, or power management.
- Some registers vary by generation/media tile; users must select the correct macro for platform context.

Test signals:
- Firmware load/status tests validate `GUC_STATUS` and scratch usage.
- Interrupt/doorbell tests validate `GUC_SEND_INTERRUPT`, doorbell register programming, and `GUC_INTR_*` handling paths.
- Platform bring-up should review any new GuC IP register changes against this header.
