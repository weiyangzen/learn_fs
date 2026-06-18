# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0_3.h

## Purpose

`mmsch_v4_0_3.h` defines a revised MMSCH 4.0.3 init-header layout for hardware with one VCN table and multiple MJPEG decoder table entries. It reuses the command ABI from `mmsch_v4_0.h`.

## Important APIs, Types, And Functions

The header includes `amdgpu_vcn.h` and `mmsch_v4_0.h`, then declares `struct mmsch_v4_0_3_init_header` with `version`, `total_size`, `vcn0`, `mjpegdec0[4]`, and `mjpegdec1[4]`, each using `struct mmsch_v4_0_table_info`.

## Control Flow

There is no executable flow. VCN/JPEG v4.0.3 callers instantiate this header, fill table metadata, and use v4.0 command macros from the included base header to populate individual engine command streams.

## State And Persistence Behavior

The header defines only the firmware-visible memory layout. It records table offsets, sizes, and init status for one VCN block and two groups of four MJPEG decoders. State persists in the command table memory until firmware consumes and updates it.

## Dependencies And Integration Points

`vcn_v4_0_3.c` and `jpeg_v4_0_3.c` include this header. It depends on `mmsch_v4_0.h` for command structures and table-info definitions, keeping the command encoding consistent while changing only the top-level table layout.

## Risks

Array sizes are ABI constraints. Using the base v4.0 header for this hardware would lose per-MJPEG metadata, while using this header for a different decoder count would misalign firmware parsing. Because it imports v4.0 macros, it inherits their caller-scope and bounds-check risks.

## Test Signals

Test VCN v4.0.3 and JPEG v4.0.3 initialization, verify all eight MJPEG table-info entries are filled and status is read back, and run decode workloads that exercise both decoder groups.
