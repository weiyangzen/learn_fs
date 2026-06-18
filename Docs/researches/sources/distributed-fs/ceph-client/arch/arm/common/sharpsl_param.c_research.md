<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/sharpsl_param.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/sharpsl_param.c

## Purpose
Early boot helper for preserving manufacturing hardware parameters from Sharp SL-series bootloader memory before the kernel overwrites them.

## Important APIs/types/functions
- Exported global `struct sharpsl_param_info sharpsl_param`.
- `sharpsl_save_param()` copies from `PARAM_BASE`.
- Magic constants: `COMADJ_MAGIC`, `UUID_MAGIC`, `TOUCH_MAGIC`, `AD_MAGIC`, and `PHAD_MAGIC`.

## Control flow
`sharpsl_save_param()` maps or directly references `PARAM_BASE`, copies the full parameter structure, and invalidates individual fields by setting them to `-1` when their keyword magic does not match.

## State and persistence behavior
The copied `sharpsl_param` global persists for the lifetime of the booted kernel. It preserves bootloader/manufacturing data in RAM; no disk state is written.

## Dependencies and integration points
Depends on `asm/mach/sharpsl_param.h`, Sharp SL board early init calling `sharpsl_save_param()`, and consumers such as LCD, touch, battery/AD, UUID, or calibration drivers.

## Risks and edge cases
Must be called before the parameter memory is overwritten. Physical address differs for SA1100 versus other platforms. Field invalidation is per-magic, so structure layout mismatches can silently produce wrong calibration.

## Test signals
Boot Sharp SL devices and verify exported calibration/UUID fields; test missing/bad magic values produce `-1` sentinel fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/sharpsl_param.c -->
