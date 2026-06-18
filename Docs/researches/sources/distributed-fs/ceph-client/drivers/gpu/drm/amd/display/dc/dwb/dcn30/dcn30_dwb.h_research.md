# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dwb/dcn30/dcn30_dwb.h

## Purpose

`dcn30_dwb.h` defines the DCN3.0 Display Writeback Controller register map, field map, object layout, and exported operations. It covers DWB top registers, scaler registers, CRC/backpressure/host-read control, output control, gamut remap, and OGAM RAM A/B programming fields.

## Important APIs, Types, And Functions

Important definitions include `TO_DCN30_DWBC`, `DWBC_COMMON_REG_LIST_DCN30`, `DWBC_COMMON_MASK_SH_LIST_DCN30`, `DWBC_REG_FIELD_LIST_DCN3_0`, `struct dcn30_dwbc_registers`, `struct dcn30_dwbc_mask`, `struct dcn30_dwbc_shift`, `struct dcn30_dwbc`, and declarations for DWB lifecycle, FC, denorm, HDR multiplier, gamut remap, and OGAM transfer function APIs.

## Control Flow

The header supplies macro-expanded register tables and typed shift/mask structs. Implementation files use these through `REG`, `FN`, and `REG_UPDATE` helpers. There is no runtime flow in the header itself.

## State, Dependencies, Risks, And Test Signals

It defines the `struct dcn30_dwbc` software object holding base `dwbc`, register table, shifts, and masks. Runtime state is hardware register state. It is consumed by DCN30 DWB implementation, DCN35 extension, generated ASIC resource files, and DWB color management. Risks include macro/list drift, missing declarations hidden in huge field lists, and wrong register ordering. Build coverage plus register-level write/read tests for FC, output control, gamut remap, and OGAM RAM A/B are critical.
