# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/regs/xe_guc_regs.h

## Purpose

`xe_guc_regs.h` is the Xe driver's GuC/HuC MMIO register contract. It names GuC boot/status registers, WOPCM and DMA programming registers, soft-scratch windows, doorbell registers, GuC interrupt masks/vectors, VF-visible host interrupt registers, and the hardware doorbell cacheline format used by GuC submission and SR-IOV code.

## Important APIs, Types, and Definitions

- GuC boot/authentication definitions: `GUC_STATUS`, `BOOT_HASH_CHK`, `GUC_HEADER_INFO`, `GS_AUTH_STATUS_*`, `GS_BOOTROM_*`, and `GUC_BOOT_UKERNEL_VALID`.
- WOPCM/DMA programming definitions: `GUC_WOPCM_SIZE`, `DMA_ADDR_*`, `DMA_COPY_SIZE`, `DMA_CTRL`, `DMA_GUC_WOPCM_OFFSET`, and the WOPCM/GGTT address-space field values.
- Doorbell definitions: `DIST_DBS_POPULATED`, `DRBREGL()`, `DRBREGU()`, `DRB_VALID`, `GT_DOORBELL_ENABLE`, `GUC_NUM_DOORBELLS`, and `struct guc_doorbell_info`.
- Interrupt definitions: `GUC_SEND_INTERRUPT`, `GUC_INTR_CHICKEN`, `GUC_*_IER`, `GUC_INTR_*`, `GUC_HOST_INTERRUPT`, `MED_GUC_HOST_INTERRUPT`, and VF software flag ranges.
- TLB invalidation definitions: `GUC_TLB_INV_CR`, `PVC_GUC_TLB_INV_DESC0`, and `PVC_GUC_TLB_INV_DESC1`.

## Control Flow

This header has no executable control flow. Its macros are consumed by GuC firmware loading, HuC loading, submission, interrupt, TLB invalidation, relay/SR-IOV, and doorbell management code. The call flow is indirect: production code builds `struct xe_reg` constants through `XE_REG()`, then passes those constants to Xe MMIO helpers for read/write or poll loops.

## State and Persistence Behavior

The header defines persistent hardware state rather than software-owned state. Doorbell register validity, GuC boot/auth fields, WOPCM lock bits, interrupt enable bits, DMA control, scratch registers, and VF-visible flags persist in MMIO until firmware, reset, or driver reprogramming changes them. `struct guc_doorbell_info` is a packed shared-memory layout with status/cookie fields monitored by hardware.

## Dependencies and Integration Points

It depends on `regs/xe_reg_defs.h` for `XE_REG()` and on Linux bitfield helpers. It integrates with GuC firmware upload/authentication, HuC load verification, GuC CT and submission code, interrupt setup, SR-IOV PF/VF communication paths, and tests such as PF GT resource partitioning that rely on `GUC_NUM_DOORBELLS`.

## Risks and Edge Cases

- Register offsets and bit encodings are silent ABI with hardware and firmware; a wrong value usually becomes a boot, interrupt, or submission failure rather than a compile error.
- `GUC_TLB_INV_CR` is defined twice in this file with the same address and bit; this is benign if identical but creates drift risk if one copy is edited later.
- VF-accessible registers must retain `XE_REG_OPTION_VF` tags where VF paths use generic MMIO validation.
- `struct guc_doorbell_info` is packed and fixed-size; adding fields or changing alignment would break hardware-monitored cacheline semantics.

## Test Signals

Compile coverage catches missing macros but not semantic offset errors. Useful signals include GuC firmware boot/auth success, HuC load success, interrupt delivery from GuC to host, doorbell allocation/activation tests, SR-IOV PF resource tests for doorbell counts, and TLB invalidation completion on platforms using the PVC descriptors.
