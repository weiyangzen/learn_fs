# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wa.h

## Purpose

`xe_wa.h` declares the hardware workaround processing interface and active OOB workaround query macros.

## Important APIs, Types, and Functions

Declared functions include `xe_wa_device_init()`, `xe_wa_gt_init()`, `xe_wa_process_device_oob()`, `xe_wa_process_gt_oob()`, `xe_wa_process_gt()`, `xe_wa_process_engine()`, `xe_wa_process_lrc()`, `xe_wa_apply_tile_workarounds()`, `xe_wa_device_dump()`, and `xe_wa_gt_dump()`. The macros `XE_GT_WA(gt__, id__)`, `XE_DEVICE_WA(xe__, id__)`, and `XE_DEVICE_WA_DISABLE(xe__, id__)` query or clear generated OOB active bits after asserting that OOB processing was initialized.

## Control Flow and State

The header itself has no state, but its macros read and modify `wa_active.oob` bitsets stored on GT or device objects. Initialization must allocate bitsets before processing, and processing must set `oob_initialized` before callers query active OOB workaround bits.

## Dependencies and Integration Points

The header includes `xe_assert.h` and uses generated enum names from generated WA headers indirectly through macro token pasting. It is consumed by device setup, GT setup, engine setup, VM creation, tile programming, and any code path that needs to branch on an OOB workaround.

## Risks and Edge Cases

Calling `XE_GT_WA()` or `XE_DEVICE_WA()` before OOB initialization triggers assertions. Macro ids must match generated names exactly. `XE_DEVICE_WA_DISABLE()` mutates active state and should be used only for deliberate runtime disabling.

## Test Signals

Build coverage validates generated id token names. Runtime tests should verify OOB initialization assertions, active bit queries for known WA/platform matches, and controlled disabling through `XE_DEVICE_WA_DISABLE()`.
