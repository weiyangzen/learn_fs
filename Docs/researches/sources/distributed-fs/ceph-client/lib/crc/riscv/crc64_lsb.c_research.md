# sources/distributed-fs/ceph-client/lib/crc/riscv/crc64_lsb.c

## Purpose
This file instantiates the RISC-V CLMUL template for reflected 64-bit CRCs, specifically the CRC64 NVMe path.

## Important APIs, Types, and Functions
It uses `typedef u64 crc_t`, `#define LSB_CRC 1`, includes the template, and defines `crc64_lsb_clmul()`.

## Control Flow
The wrapper returns `crc_clmul(crc, p, len, consts)`, with all actual folding and reduction in the template.

## State and Persistence
No persistent state exists.

## Dependencies and Integration Points
It is compiled only where 64-bit RISC-V CRC64 support is available and is called by `crc64_nvme_arch()`.

## Risks and Test Signals
Risks are reflected 64-bit polynomial reductions and ABI availability under `CONFIG_64BIT`. CRC64 NVMe KUnit coverage and large-buffer tests are important.
