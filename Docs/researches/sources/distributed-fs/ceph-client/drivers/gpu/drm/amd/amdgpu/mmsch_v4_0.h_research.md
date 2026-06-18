# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0.h

## Purpose

`mmsch_v4_0.h` defines the MMSCH 4.0 init-table ABI for VCN/JPEG generation 4 media virtualization. It extends the VCN instance table with JPEG decoder table metadata and mailbox/status constants used by VF media initialization.

## Important APIs, Types, And Functions

The header defines version macros, ring-buffer enable flags `RB_ENABLED` and `RB4_ENABLED`, VF engine status and mailbox response constants, `MMSCH_V4_0_VCN_INSTANCES`, command-type enum, `mmsch_v4_0_table_info`, `mmsch_v4_0_init_header`, command structs, and insertion macros for read-modify-write, write, poll, and end commands.

## Control Flow

It has no independent flow. Callers such as VCN/JPEG v4 code create headers and command tables, then use macros to append commands to `table_loc`. Each macro copies one command struct and advances the caller's location and size counters.

## State And Persistence Behavior

The init header persists per-engine table metadata for two VCN instances and one JPEG decoder table. Mailbox response constants encode firmware-visible completion states such as OK, incomplete, failed, small context, and unknown command. The macros mutate caller-local command table construction variables only.

## Dependencies And Integration Points

It includes `amdgpu_vcn.h` and is used by `vcn_v4_0.c`, `vcn_v4_0_5.c`, `jpeg_v4_0.c`, and `jpeg_v4_0_5.c`. `mmsch_v4_0_3.h` also includes it to reuse table-info and command structures with a revised header layout.

## Risks

ABI compatibility with MMSCH firmware is the main risk. The macros are not bounds-checked and require specific caller variable names. The generic v4.0 header supports only a single `jpegdec` table; later hardware with multiple MJPEG decoders must use the v4.0.3-specific header instead.

## Test Signals

Validate VCN/JPEG v4 SR-IOV initialization, VF mailbox response handling, ring-buffer enable flags, command-table total sizes, and media decode/encode smoke tests after MMSCH setup.
