# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_metadata.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_metadata.h` is the public metadata buffer layout and allocation API in the Intel AtomISP CSS driver. It defines metadata configuration, computed metadata layout, and `struct ia_css_metadata` with CSS virtual address and exposure id.

## Important APIs, Types, and Functions

Visible functions: none visible in this file. Visible structs: `struct ia_css_metadata_config`, `struct ia_css_resolution  resolution; /** Resolution */`, `struct ia_css_metadata_info`, `struct ia_css_resolution resolution; /** Resolution */`, `struct ia_css_metadata`, `struct ia_css_metadata_info info;    /** Layout info */`, `struct ia_css_metadata *`. Visible enums: `enum atomisp_input_format data_type; /** Data type of CSI-2 embedded`. Important macros/constants: `__IA_CSS_METADATA_H`, `SIZE_OF_IA_CSS_METADATA_STRUCT`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Streams use `ia_css_metadata_config` to describe embedded CSI-2 metadata, derive `ia_css_metadata_info`, then allocate/free CSS-addressed metadata buffers through `ia_css_metadata_allocate()` and `ia_css_metadata_free()`.

## State and Persistence Behavior

The struct is a host handle to CSS memory; persistence is tied to explicit allocation and free. Exposure id travels with the buffer to correlate metadata with frames.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risk is size/stride mismatch for embedded formats and lifetime mistakes around the CSS virtual address. Tests should cover embedded data formats, zero/large metadata sizes, and allocation failure.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 68 lines, 2051 bytes.
