# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/i9xx_display_sr.h

## Purpose
`i9xx_display_sr.h` is the small public header for legacy i9xx display save/restore helpers.

## Important APIs, Types, and Functions
It forward-declares `struct intel_display` and declares `i9xx_display_sr_save()` and `i9xx_display_sr_restore()`. These functions snapshot and replay legacy display register state in the C file.

## Control Flow and State
No state is stored in the header. The function pair implies a caller-managed lifecycle: call save before suspend/reset state loss and restore after display MMIO/PCI config can be programmed again.

## Dependencies and Integration Points
The header has no includes beyond the guard and is intended for higher-level display power-management code. The implementation depends on `display->restore` storage in `struct intel_display`.

## Risks and Test Signals
Risk is limited to declaration drift and misuse of save/restore ordering by callers. Build coverage and suspend/resume tests of the implementation provide validation.
