# sources/distributed-fs/ceph-client/include/linux/firmware/broadcom/tee_bnxt_fw.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware/broadcom/tee_bnxt_fw.h` declares Broadcom BNXT firmware operations mediated through a Trusted Execution Environment. The source was read as a complete 14-line file for this report.

## Important APIs, Types, and Functions

The APIs are `tee_bnxt_fw_load()` and `tee_bnxt_copy_coredump(void *buf, u32 offset, u32 size)`.

## Control Flow

BNXT driver code can request secure firmware loading through TEE and copy coredump ranges from secure/firmware-owned storage into a caller buffer.

## State and Persistence Behavior

The header owns no state. Firmware and coredump state are managed by the BNXT driver, TEE client, and device/secure firmware.

## Dependencies and Integration Points

It depends on `linux/types.h` and integrates with Broadcom network firmware loading, TEE infrastructure, and coredump retrieval paths.

## Risks and Edge Cases

Coredump offset/size validation and secure memory access are critical. Loading failures may depend on TEE availability and firmware policy.

## Test Signals

BNXT firmware load tests with and without TEE, coredump range tests, secure firmware error injection, and build coverage for BNXT TEE integration.
