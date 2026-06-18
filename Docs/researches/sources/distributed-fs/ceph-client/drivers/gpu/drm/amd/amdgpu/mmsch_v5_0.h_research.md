# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v5_0.h

## Purpose

`mmsch_v5_0.h` defines the MMSCH 5.0 command-table ABI for newer VCN/JPEG generation 5 media virtualization. It is structurally similar to v4.0.3 but increases MJPEG decoder table capacity to five entries per group and uses version 5.0 identifiers.

## Important APIs, Types, And Functions

It includes `amdgpu_vcn.h`, defines version, ring-buffer, VF engine status, and mailbox response constants, declares `enum mmsch_v5_0_command_type`, `struct mmsch_v5_0_table_info`, `struct mmsch_v5_0_init_header`, command structs, and macros `MMSCH_V5_0_INSERT_DIRECT_RD_MOD_WT`, `MMSCH_V5_0_INSERT_DIRECT_WT`, `MMSCH_V5_0_INSERT_DIRECT_POLL`, and `MMSCH_V5_0_INSERT_END`.

## Control Flow

Callers build command tables by filling a v5.0 header and appending command structs through macros. The macros compute command size, copy from caller-local command templates into `table_loc`, and update dword counts.

## State And Persistence Behavior

The init header stores firmware-visible metadata for `vcn0`, `mjpegdec0[5]`, and `mjpegdec1[5]`. Mailbox constants represent firmware response state. The header itself stores no persistent kernel state; caller-created tables and firmware-updated init status carry runtime state.

## Dependencies And Integration Points

`vcn_v5_0_1.c`, `jpeg_v5_0_1.c`, and `jpeg_v5_0_2.c` include this header. The command layout must match MMSCH 5.0 firmware expectations.

## Risks

Macro hygiene and no bounds checks remain risks. Command-type fields and `end` command initialization are caller responsibilities. The five-entry MJPEG arrays are fixed ABI assumptions and should not be reused for variants with different decoder counts without a new header.

## Test Signals

Test generation 5 VCN/JPEG VF initialization, verify header total size and all MJPEG table statuses, validate mailbox response handling, and run media workloads after table submission. Build coverage should include all v5 macro callers.
