# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_types.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_types.h` is the central public CSS data-type and ISP configuration header in the Intel AtomISP CSS driver. It defines core scalar types, resolutions, coordinates, data handles, shading/grid/morph/DVS/zoom/capture structures, and the large `struct ia_css_isp_config` pointer bundle for ISP filter settings.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_isp_parameters;`, `struct ia_css_pipe;`, `struct ia_css_memory_offsets;`, `struct ia_css_config_memory_offsets;`, `struct ia_css_state_memory_offsets;`, `struct ia_css_resolution`, `struct ia_css_coordinate`, `struct ia_css_vector`, `struct ia_css_data`, `struct ia_css_host_data`. Visible enums: `enum ia_css_shading_correction_type`, `enum ia_css_shading_correction_type type; /** Shading Correction type. */`, `enum ia_css_vamem_type vamem_type;`, `enum ia_css_capture_mode`, `enum ia_css_capture_mode mode; /** Still capture mode */`. Important macros/constants: `_IA_CSS_TYPES_H`, `IA_CSS_DVS_STAT_GRID_INFO_SUPPORTED`, `IA_CSS_VERSION_MAJOR`, `IA_CSS_VERSION_MINOR`, `IA_CSS_VERSION_REVISION`, `IA_CSS_MORPH_TABLE_NUM_PLANES`, `IA_CSS_ISYS_MIN_EXPOSURE_ID`, `IA_CSS_ISYS_MAX_EXPOSURE_ID`, `SIZE_OF_IA_CSS_PTR`, `IA_CSS_ISP_DMEM`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Most public pipe and stream APIs include this header; parameter setters copy pointed-to config structs into `ia_css_isp_parameters`, while shading and morph tables are documented as pointer-copied.

## State and Persistence Behavior

State is caller-owned unless copied by a setter. Tables and buffers referenced by pointer need explicit lifetime management across pipe/stream use.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are ABI drift, shallow pointer lifetime bugs, default macro omissions, and coordinate normalization regressions across digital zoom, DVS, shading, and face/3A windows.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 596 lines, 24146 bytes.
