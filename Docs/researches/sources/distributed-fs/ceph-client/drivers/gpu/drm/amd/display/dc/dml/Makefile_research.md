# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/Makefile

## Purpose
Builds the Display Mode Library objects and applies per-object compiler flags required for floating-point DML code inside the AMD display driver. It selectively adds DML objects when `CONFIG_DRM_AMD_DC_FP` is enabled and appends them to `AMD_DISPLAY_FILES`.

## Important APIs, Types, And Functions
Important variables include `dml_ccflags` for FPU-enabled compile flags, `dml_rcflags` for flags to remove, optional `frame_warn_flag`, `DML` object list, `AMD_DAL_DML`, and final `AMD_DISPLAY_FILES` augmentation. It applies `CFLAGS_...` and `CFLAGS_REMOVE_...` to DML core, VBA, RQ/DLG, FPU, DSC, and calculator objects.

## Control Flow
Makefile logic computes a frame warning threshold when `CONFIG_FRAME_WARN` is nonzero, with special handling for KASAN/KCSAN and Clang compile testing. It assigns FPU flags per object and removes no-FPU flags from those objects. Under `CONFIG_DRM_AMD_DC_FP`, it builds a long list of DML objects across DCN10-DCN35 and calculator code, prefixes paths with `$(AMDDALPATH)/dc/dml/`, then appends to `AMD_DISPLAY_FILES`.

## State And Persistence
The file persists build configuration through make variables only. It does not produce runtime state directly, but it controls which object files exist in the driver binary and which warning/FPU flags apply.

## Dependencies And Integration Points
Depends on top-level AMD display make variables such as `AMDDALPATH`, `CC_FLAGS_FPU`, `CC_FLAGS_NO_FPU`, `CONFIG_DRM_AMD_DC_FP`, `CONFIG_FRAME_WARN`, `CONFIG_KASAN`, `CONFIG_KCSAN`, `CONFIG_CC_IS_CLANG`, `CONFIG_COMPILE_TEST`, and `test-lt`. It integrates every DML generation-specific source into the AMD display build.

## Risks
Incorrect FPU/no-FPU flag handling can break kernel build rules or produce invalid floating-point usage. Frame warning thresholds are tuned for sanitizer/compiler combinations; too-low limits can fail builds due to large generated DML stack frames. Duplicate `CFLAGS_REMOVE` entries appear intentional but are fragile. Missing new DML objects from `DML` means code compiles locally but is absent from the driver.

## Test Signals
Kernel builds with and without `CONFIG_DRM_AMD_DC_FP`, GCC and Clang compile tests, KASAN/KCSAN configurations, frame warning behavior, and link validation that all referenced DML objects are included exactly as expected.
