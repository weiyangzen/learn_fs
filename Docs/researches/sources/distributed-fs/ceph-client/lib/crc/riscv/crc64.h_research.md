# sources/distributed-fs/ceph-client/lib/crc/riscv/crc64.h

## Purpose
This arch header provides RISC-V Zbc acceleration hooks for CRC64 BE and CRC64 NVMe.

## Important APIs, Types, and Functions
It defines `crc64_be_arch()` and `crc64_nvme_arch()`. They call `crc64_msb_clmul()` with the ECMA polynomial constants or `crc64_lsb_clmul()` with the NVMe reflected constants when Zbc is likely present.

## Control Flow
Each hook performs a runtime Zbc feature check and either dispatches to the CLMUL function or falls back to `crc64_be_generic()`/`crc64_nvme_generic()`.

## State and Persistence
No mutable state is introduced. Feature state is handled by RISC-V CPU capability code.

## Dependencies and Integration Points
It depends on 64-bit RISC-V declarations from `crc-clmul.h`; the corresponding constant objects are only defined under `CONFIG_64BIT`.

## Risks and Test Signals
Risks include accidental use in 32-bit builds, reflected NVMe inversion convention mismatches, and runtime feature misdetection. CRC64 KUnit random tests, especially CRC64 NVMe wrapper tests, are the main validation signal.
