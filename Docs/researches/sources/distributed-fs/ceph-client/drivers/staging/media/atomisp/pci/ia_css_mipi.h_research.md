# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mipi.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/ia_css_mipi.h` is the public MIPI frame sizing helper interface in the Intel AtomISP CSS driver. It declares `ia_css_mipi_frame_calculate_size()` for converting width, height, atomisp input format, optional SOL/EOL packets, and embedded-data words into a 32-byte-memory-word frame size.

## Important APIs, Types, and Functions

Visible functions: `ia_css_mipi_frame_calculate_size`. Visible structs: none visible in this file. Visible enums: none visible in this file. Important macros/constants: `__IA_CSS_MIPI_H`.

The file's important contract is the relationship between these declarations and the surrounding CSS stream, pipe, binary, input-system, or hardware register code.

## Control Flow

Callers use it before allocating buffered-sensor/MIPI capture buffers. The function is expected to validate unsupported formats and return an error code rather than writing a bogus size.

## State and Persistence Behavior

There is no persistent state. The output size feeds later buffer allocation and DMA programming.

## Dependencies and Integration Points

It integrates with the AtomISP PCI staging driver, CSS firmware/binary metadata, HRT/system-local hardware definitions, and the public pipe/stream/config APIs as applicable. Headers in this group are often ABI-like: their struct layout, enum order, or register indexes must match generated code and firmware expectations.

## Risks and Edge Cases

Risks are integer overflow, off-by-one packing for RAW/compressed formats, and confusion between bytes, pixels, and 32-byte memory words.

## Test Signals

Useful signals include AtomISP build coverage, stream/pipe creation and teardown, ISP parameter update with the relevant config pointer populated and omitted, firmware binary metadata with zero and nonzero offsets, and hardware or emulated input-system/MMU/IRQ paths for register-defined headers. Source read size: 39 lines, 1213 bytes.
