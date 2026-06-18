# subset-b-001420 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/Makefile -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/cmntypes.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/cmntypes.h

## Purpose

`cmntypes.h` is a compact DML2 compatibility header that defines legacy-style scalar aliases, pointer aliases, and small color packing types used by the AMD display mode library code. It is included through DML-facing headers such as `dml_depedencies.h` and `display_mode_util.h`, making it part of the shared type surface for DML2 calculation and utility code.

The header has no functions and no executable logic beyond preprocessor guards. Its role is to stabilize names such as `uint8`, `uint32`, `pvoid`, `rgba_t`, and `gen_color_u` for code imported from or shared with display-mode calculation tooling that does not consistently use kernel fixed-width typedef names directly.

## Important APIs, types, and definitions

- Header guard: `__CMNTYPES_H__` prevents repeated typedef definitions across DML2 include chains.
- GCC-specific `uint` typedef guard: for GCC 4 with minor version greater than 7, it conditionally defines `typedef unsigned int uint;`; the file later defines `uint` unconditionally as well.
- Signed scalar and pointer aliases: `int8`/`pint8`, `int16`/`pint16`, `int32`/`pint32`, and `int64`/`pint64`.
- Unsigned scalar and pointer aliases: `uint8`/`puint8`, `uint16`/`puint16`, `uint32`/`puint32`, and `uint64`/`puint64`.
- Additional aliases: `ulong`, `uchar`, `uint`, `pvoid`, `pchar`, `const_pvoid`, and `const_pchar`.
- `rgba_t`: byte-ordered struct with `a`, `r`, `g`, and `b` members.
- `gen_color_t`: byte-ordered struct with `blue`, `green`, `red`, and `alpha` members.
- `gen_color_u`: union exposing the same 32-bit color value as either `uint32 val` or structured `gen_color_t f`.
- Disabled `#if 0` block: contains historical `uintfloat32`, `uintfloat64`, and `UNREFERENCED_PARAMETER` definitions for bit-level float/double access, but they are not compiled.

## Control flow

Include-time control flow is minimal. The header guard admits the file once, then a GCC version check may provide `uint` for a narrow compiler range. The rest of the active file is a sequence of typedefs and color type declarations. The disabled block documents older or optional helpers for floating-point bit reinterpretation but has no build effect.

There are no callbacks, macros with side effects, inline functions, allocation paths, or runtime branches. All behavior is compile-time type publication.

## State and persistence behavior

The header creates no runtime state and stores nothing persistently. Its "state" is C translation-unit type state: once included, all downstream code can use these aliases and color layouts. The color union provides an in-memory representation contract for code that wants either packed 32-bit access or named byte channels, so byte ordering and struct field order matter for callers that interpret `gen_color_u.val`.

## Dependencies and integration points

The file depends only on compiler built-ins for `__GNUC__` and basic C typedef syntax. It does not include Linux kernel headers such as `<linux/types.h>`, so definitions like `signed int64` and `unsigned uint64` assume compatible typedefs or macros for `int64`/`uint64` already exist before this header is parsed, or that the compiler accepts those names from the broader AMD display include environment.

Within this tree, `dml_depedencies.h` and `display_mode_util.h` include `cmntypes.h`, which makes the aliases visible to DML2 display-mode core, DML utility code, and dependent DML21 translation/helper modules. The color types can be used wherever DML code needs a small packed ARGB/BGRA-style representation without depending on DRM or kernel color structs.

## Risks and edge cases

- The typedefs intentionally use common names such as `uint`, `ulong`, and `uchar`; these can collide with other platform, kernel, or compiler-provided aliases if include order changes.
- `typedef signed int64, *pint64;` and `typedef unsigned uint64, *puint64;` are unusual because `int64` and `uint64` are used as base type specifiers rather than introduced from fixed-width kernel types in this header. Portability depends on the surrounding AMD display headers defining those names or on accepted compiler extensions.
- The conditional GCC `uint` typedef is redundant with the later unconditional `typedef unsigned int uint;`; if another header already defined `uint` differently, this file can create redefinition errors.
- `gen_color_u` overlays a `uint32` with four bytes. Channel interpretation is sensitive to endian layout when code serializes or compares the packed `val`.
- Pointer aliases such as `pvoid`, `pchar`, and `puint32` reduce type clarity and can hide const-correctness issues in older imported code.
- The disabled float bit-cast unions suggest historical need for bit reinterpretation. Re-enabling them would need strict-aliasing and kernel FPU review.

## Test signals

Compile coverage is the main signal: any typedef collision or missing prerequisite for `int64`/`uint64` should surface when building DML2 users such as `display_mode_util.c`, `display_mode_core.c`, `dml2_wrapper_fpu.c`, and DML21 translation/helper code. Cross-compiler builds are useful because this header has compiler-version conditional code and nonstandard-looking typedefs.

Runtime-adjacent validation should focus on code paths that consume `gen_color_u` or these scalar aliases in display-mode calculations. Useful signals include successful DML2/DML21 mode validation, color/debug paths that pack and unpack generated colors, and absence of endian-sensitive mismatches in diagnostics or programmed values. Static analysis can also flag alias collisions, unused legacy typedefs, and include-order dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/cmntypes.h -->
