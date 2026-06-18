# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_ctrl_regs.h

## Purpose

`mme2_ctrl_regs.h` is an auto-generated hardware register address map for the Gaudi MME2 control block, marked as prototype `MME`. It exposes 717 `#define` constants whose names begin with `mmMME2_CTRL_`, covering the MME2 descriptor/programming surface from `mmMME2_CTRL_ARCH_STATUS` at `0x160000` through `mmMME2_CTRL_SHADOW_3_DESC_DUMMY` at `0x160DA4`. It contains no executable code; its value is the stable ABI between the driver and the MME2 memory-mapped register file.

## Important APIs, types, and functions

There are no C functions, structs, enums, or inline helpers. The only exported interface is preprocessor constants included indirectly through `include/gaudi/asic_reg/gaudi_regs.h`. The macro families are the API:

- `ARCH_*` registers describe the active MME descriptor image: status, base addresses for S/L/O tensors, descriptor headers, convolution fields, iteration controls, tensor valid-elements/loop-stride/ROI/spatial fields, AGU offsets, sync-object fields, AXI-user data, performance event selectors, padding values, metadata, rate limiter, and dummy descriptor words.
- `SHADOW_0_*` through `SHADOW_3_*` replicate the same descriptor layout for four shadow descriptor slots. The file has 548 shadow defines and 137 active `ARCH_*` defines, so the shadow banks dominate the address surface.
- Non-descriptor control/debug registers include `CMD`, `RESET`, `PROT`, interrupt cause/mask, `QM_SLV_*`, `QM_STALL`, `AGU_SYNC`, `AGU_SM`, `TE_CLOSE`, PCU rate-limiter/dummy registers, EUS rollup, power-control, sync object, and CoreSight-adjacent base registers referenced from other generated headers.

## Control flow

The header has no runtime control flow. Driver control flow appears where consumers write or read these addresses using low-level accessors such as `WREG32()` and `RREG32()`. In `gaudi.c`, MME2-related initialization and enablement are paired with the MME2 QMAN registers; in `gaudi_coresight.c`, MME2 control block base constants are used to enumerate trace/debug components. The intended hardware flow is descriptor programming into `ARCH_*` or shadow banks, command/queue interaction via QMAN, then status, interrupt, and debug reads.

## State and persistence behavior

The macros themselves are compile-time constants and persist only in the built driver image. The state they name is volatile device state in the Gaudi MME2 control register file. Writes to descriptor, AGU, padding, metadata, sync-object, and rate-limiter addresses program hardware behavior until reset, reprogramming, or power management clears it. Shadow descriptor banks are especially stateful: changing a generated address in one bank can silently redirect a descriptor field to the wrong hardware slot.

## Dependencies and integration points

The direct include path is `gaudi_regs.h`, which is then used by Gaudi driver code and common Gaudi mask definitions. This header must stay synchronized with other MME headers and block base definitions. `mme3_ctrl_regs.h` has the same normalized layout with an `MME3` prefix and a base range of `0x1E0000`; this MME2 file is the `0x160000` instance. Integration points include MME engine setup, descriptor construction code that emits register writes, interrupt/debug handling, power-management sequences, and CoreSight lookup tables.

## Risks

The main risk is address drift from hardware documentation or generated source: no compiler type checking can detect a semantically wrong register address. Because the file repeats many similarly named tensor/AGU/descriptor fields across active and shadow banks, off-by-one generation errors or prefix/base mismatches can be difficult to diagnose. MME2/MME3 symmetry is useful but also risky: copying an MME3 define into MME2 logic would compile while touching the wrong hardware range. Since this file carries only addresses, field-width validation must come from matching mask headers or hardware tests.

## Test signals

Useful signals are build coverage for all includes, probe/init success on Gaudi hardware, MME queue execution tests, descriptor programming tests that exercise S/L/O tensors and shadow descriptors, interrupt/status tests around `INTR_CAUSE` and `ARCH_STATUS`, and debug tooling that confirms CoreSight/base-address tables resolve MME2 blocks correctly. Static checks can compare the normalized MME2 and MME3 layouts and assert that the base delta remains intentional.
