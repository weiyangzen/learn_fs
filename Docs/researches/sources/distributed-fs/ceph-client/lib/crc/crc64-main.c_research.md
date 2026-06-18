# sources/distributed-fs/ceph-client/lib/crc/crc64-main.c

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/crc64-main.c` implements generic CRC64 ECMA big-endian and CRC64-NVME reflected variants, with optional architecture dispatch.

## Important APIs, Types, and Functions

Exported GPL APIs are `crc64_be(u64 crc, const void *p, size_t len)` and `crc64_nvme(u64 crc, const void *p, size_t len)`. Internal generic helpers are `crc64_be_generic` and `crc64_nvme_generic`. The file includes generated `crc64table.h`.

## Control Flow

The ECMA helper shifts left and indexes `crc64table` with the high byte. The NVME helper shifts right and indexes `crc64nvmetable` with the low byte. With architecture support, `$(SRCARCH)/crc64.h` defines arch wrappers; otherwise they alias to generic. The exported NVME function complements the input and output around `crc64_nvme_arch()`.

## State and Persistence Behavior

Lookup tables are generated read-only data. Arch dispatch may use static feature state in included headers. Per-call CRC state is by value.

## Dependencies and Integration Points

Dependencies include `linux/crc64.h`, generated table headers, module exports, and arch implementations for ARM64, RISCV, or X86 when selected. NVME and other storage code consume the reflected variant.

## Risks and Edge Cases

ECMA and NVME variants differ in polynomial and bit order. The complement convention for NVME must remain at the exported wrapper boundary. Architecture acceleration currently may cover only one variant, as arm64 accelerates NVME but not ECMA.

## Test Signals

Signals include ECMA and NVME known vectors, zero-length complement behavior for NVME, chunked equivalence, generated table regeneration, and generic-vs-arch comparisons.

## Read Coverage

Source read size: 93 lines, 2654 bytes.
