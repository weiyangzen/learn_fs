# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/firmware/riscv.rs

## Purpose

`firmware/riscv.rs` parses firmware binaries designed for NVIDIA RISC-V cores, especially the GSP bootloader used during main GSP startup.

## Important APIs, Types, And Functions

`RmRiscvUCodeDesc` mirrors the RISC-V firmware descriptor. `RiscvFirmware` stores code, data, manifest offsets, application version, and a coherent mapped firmware payload. `RiscvFirmware::new()` parses the common binary header and descriptor, then maps the payload.

## Control Flow

Construction validates the common `BinFirmware`, reads the descriptor at `header_offset`, slices the data payload using `data_offset` and `data_size`, maps it into a coherent device-visible allocation, and exposes monitor code/data/manifest offsets plus app version for boot metadata and Falcon OS version programming.

## State And Persistence Behavior

The coherent firmware payload must remain alive while GSP bootloader DMA references are used. Parsed offsets and `app_version` are immutable state copied from firmware headers.

## Dependencies And Integration Points

It depends on `BinFirmware`, kernel firmware loading, coherent DMA, transmute `FromBytes`, and safe numeric conversions. `GspFirmware` owns a `RiscvFirmware`, and `gsp/boot.rs` writes its app version into the GSP Falcon OS register.

## Risks And Test Signals

Risks include trusting descriptor offsets semantically after bounds checks, coherent allocation size matching payload size, and firmware format changes. Test with valid and malformed bootloader binaries, descriptor offset bounds, payload slicing, app-version propagation, and GSP bootloader load through WPR metadata.
