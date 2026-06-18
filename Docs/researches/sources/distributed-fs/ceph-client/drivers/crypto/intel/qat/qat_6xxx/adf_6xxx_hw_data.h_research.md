# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/adf_6xxx_hw_data.h

## Purpose
This header captures Gen6 QAT hardware constants: BAR layout, fuse offsets, bank/ring geometry, admin mailbox offsets, interrupt masks, watchdog timers, ring-pair reset CSRs, virtual-channel PCI config fields, error masks, firmware names, rate-limit constants, slice fuse bits, and the helper that detects wireless-crypto SKUs.

## Important APIs, Types, And Functions
Public declarations are `adf_init_hw_data_6xxx()` and `adf_clean_hw_data_6xxx()`. The important inline helper is `adf_6xxx_is_wcy()`, which tests `ICP_ACCEL_GEN6_MASK_WCP_WAT_SLICE` in `ADF_FUSECTL1`. The `enum icp_qat_gen6_slice_mask` names fuse bits used to remove advertised capabilities.

## Control Flow
The header itself has no runtime control flow except the inline WCY predicate. Its constants drive BAR mapping in `adf_drv.c`, CSR writes and polling in `adf_6xxx_hw_data.c`, admin mailbox setup in `adf_admin.c`, and firmware loader selections.

## State And Persistence Behavior
There is no mutable state. The values become compile-time hardware contracts. Runtime state arises when the implementation writes these offsets/masks into device CSRs or populates `hw_data`.

## Dependencies And Integration Points
It includes Linux bit/time/unit helpers plus QAT acceleration/config/DC definitions. It integrates Gen6 PCI probing, firmware loading, PM, ring reset, VC setup, RAS, anti-rollback, and rate limiting.

## Risks
Wrong CSR offsets or masks can hang reset polling, misroute interrupts, break VC setup, or expose unsupported slices. The WCY predicate is a compact fuse interpretation and is high risk if hardware documentation changes.

## Test Signals
Build coverage validates declarations. Runtime signals include correct BAR mapping, successful admin mailbox communication, ring reset completion, VC config writes, watchdog programming, firmware request names, and capability exposure that changes correctly when fuse bits are set.
