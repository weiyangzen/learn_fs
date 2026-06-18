# sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_msb.c

## Purpose
This file instantiates the RISC-V CLMUL template for non-reflected 64-bit CRC64 BE.

## Important APIs, Types, and Functions
It defines `crc_t` as `u64`, sets `LSB_CRC` to `0`, includes the template, and exposes `crc64_msb_clmul()`.

## Control Flow
`crc64_msb_clmul()` is a thin wrapper over `crc_clmul()`.

## State and Persistence
All computation state is local.

## Dependencies and Integration Points
It integrates with `crc64_be_arch()` and the ECMA polynomial constants from `crc-clmul-consts.h`.

## Risks and Test Signals
Risks include MSB-first endianness, long-width assumptions, and CRC64 constant mismatch. CRC64 BE KUnit and generic cross-checks validate this path.
