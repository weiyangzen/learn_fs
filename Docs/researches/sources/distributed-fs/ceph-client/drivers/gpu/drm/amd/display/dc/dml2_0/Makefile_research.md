# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/Makefile

## Purpose

This Makefile wires the AMD Display Core DML2 and DML21 implementation into the AMDGPU display build. It contributes object files under `dc/dml2_0/` and `dc/dml2_0/dml21/` to the parent `AMD_DISPLAY_FILES` list, sets the include search path for DML2/DML21 internals, and carefully assigns floating-point versus non-floating-point compiler flags to individual translation units.

DML is display-mode library code: it computes display timing, bandwidth, watermark, power, and resource feasibility data used by DC validation paths. The build file is therefore not just a source list; it is also the boundary that keeps heavy mathematical code compiled with `CC_FLAGS_FPU` while wrapper code that can be called from normal kernel contexts is compiled with `CC_FLAGS_NO_FPU`.

## Important build variables and entries

- `dml2_ccflags := $(CC_FLAGS_FPU)` and `dml2_rcflags := $(CC_FLAGS_NO_FPU)` define the add/remove flag sets used throughout this directory.
- `frame_warn_limit` and `frame_warn_flag` derive a local `-Wframe-larger-than=` override when `CONFIG_FRAME_WARN` is nonzero and the configured threshold is lower than DML2's tolerated stack usage.
- `subdir-ccflags-y` adds include directories for the DML2 root, DML21 core, MCG, DPMM, PMO, standalone library, and public/private include trees.
- `DML2_ABS_PATH`, `DML2_C_FILES`, and `DML2_RELATIVE_O_FILES` dynamically find every C file under `dc/dml2_0`, convert it to an object path relative to `$(AMDDALPATH)`, and use `$(foreach ... $(eval ...))` to set default per-object FPU flags.
- Explicit `CFLAGS_...` overrides add `$(frame_warn_flag)` to stack-heavy math files and switch wrapper objects back to no-FPU flags.
- `DML2` lists the legacy/top-level DML2 objects: `display_mode_core.o`, `display_mode_util.o`, `dml2_wrapper_fpu.o`, `dml2_wrapper.o`, utility/policy/translation/resource/MALL phantom objects, and `dml_display_rq_dlg_calc.o`.
- `AMD_DAL_DML2 = $(addprefix $(AMDDALPATH)/dc/dml2_0/,$(DML2))` publishes those objects to `AMD_DISPLAY_FILES`.
- `DML21` lists the next-generation DML21 modules: top interfaces, SoC15 top layer, DCN4 core/factory/calculation utilities, DPMM, MCG, PMO, standalone float math, translation helper, wrapper, FPU wrapper, and DML21 utilities.
- `AMD_DAL_DML21 = $(addprefix $(AMDDALPATH)/dc/dml2_0/dml21/,$(DML21))` publishes DML21 objects to the same aggregate display build.

## Control flow

During kbuild evaluation, the parent `dc/Makefile` includes `dml2_0` through `DC_LIBS += dml2_0`. This file first establishes local compiler flag policy. If frame warnings are enabled, it selects a threshold based on sanitizer and compiler-test configuration: sanitizer builds get a larger threshold, clang compile-test sanitizer builds get the largest threshold, and non-sanitizer builds use a smaller DML2-specific limit. It only emits a local frame warning flag when the global `CONFIG_FRAME_WARN` value is lower than that local limit.

The include path is then expanded so DML2 and DML21 source files can include root, component-local, and shared DML21 headers without long relative paths. Next, the dynamic `find` pass enumerates all C files in the directory subtree and creates per-object flag assignments. The default is FPU-enabled compilation with no-FPU flags removed. A small set of wrapper objects is then explicitly flipped to no-FPU compilation, while known large-frame math objects retain FPU compilation and receive the relaxed frame-warning flag. Finally, the declarative `DML2` and `DML21` object lists are prefixed with their build paths and appended to `AMD_DISPLAY_FILES`.

## State and persistence behavior

There is no runtime state. The persistent effect is build graph and compiler-flag state inside kbuild variables. Changing this file changes which DML2/DML21 translation units are compiled into the AMD display driver, which include directories are visible to that subtree, and whether a given object is allowed to contain floating-point code.

The dynamic C-file scan means flag state can apply to new `.c` files under `dc/dml2_0` even before they are added to `DML2` or `DML21`. Those files will not be linked until listed in the object lists, but their `CFLAGS_...` entries may already exist during make evaluation.

## Dependencies and integration points

This file depends on the surrounding AMD display kbuild infrastructure defining `FULL_AMD_DISPLAY_PATH`, `AMDDALPATH`, `AMD_DISPLAY_FILES`, `CC_FLAGS_FPU`, `CC_FLAGS_NO_FPU`, `CONFIG_FRAME_WARN`, `CONFIG_KASAN`, `CONFIG_KCSAN`, `CONFIG_CC_IS_CLANG`, `CONFIG_COMPILE_TEST`, and the `test-lt` make helper. It integrates with the parent `drivers/gpu/drm/amd/display/dc/Makefile`, which includes the DML2 library directory, and with Linux kernel FPU build rules that require FPU-using code to be isolated from normal kernel call paths.

The listed objects integrate with Display Core validation and resource planning: wrappers provide non-FPU entry points, FPU wrappers/math modules perform DML calculations, translation helpers convert DC state into DML inputs, and DML21 submodules cover DCN4 core calculation, DPMM, MCG, PMO, FAMS2, and standalone math support.

## Risks and edge cases

- The `find $(DML2_ABS_PATH) -name '*.c' -type f` call runs at make evaluation time. Path mistakes or unusual build environments can silently miss files or add flags for files not intended for the current build graph.
- FPU flag correctness is critical. If wrapper files that run in no-FPU kernel contexts accidentally inherit `CC_FLAGS_FPU`, or math files lose FPU flags, the result can be build failures or unsafe kernel FPU usage.
- The explicit wrapper exceptions must stay synchronized with source-file responsibilities. New wrapper-like files need matching no-FPU overrides.
- The frame-warning relaxation is narrowly applied. New large-stack DML calculation files may fail builds under strict `CONFIG_FRAME_WARN` until added to the override list or refactored.
- Object-list omissions produce link-time missing symbols or disabled feature paths. Dynamic flag discovery does not automatically add new objects to `AMD_DISPLAY_FILES`.
- The comments use `dal/dc/dml2_0` while the actual paths are under `dc/dml2_0`; future maintainers should follow the variables rather than the stale path wording.

## Test signals

The primary test signal is successful kernel or module build coverage for AMDGPU display with DML2 enabled. Useful build variants include sanitizer and non-sanitizer builds, clang and gcc builds, compile-test builds, and strict `CONFIG_FRAME_WARN` settings. Inspecting generated command lines should show FPU flags on DML math objects, no-FPU flags on `dml2_wrapper.o` and `dml21_wrapper.o`, and the frame warning override on `display_mode_core.o`, `dml2_core_dcn4_calcs.o`, and `dml2_core_utils.o`.

Runtime signals come from modeset validation paths that exercise DML2 and DML21 calculations: multi-display bandwidth validation, DCN4 and DCN4.2 paths, PMO/FAMS2 decisions, MALL phantom/SubVP cases, and DP/HDMI timing changes. Build or boot failures around unresolved DML symbols, illegal FPU use warnings, or stack-frame warnings point back to this file's object lists and flag assignments.
