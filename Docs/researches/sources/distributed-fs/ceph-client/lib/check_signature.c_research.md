# sources/distributed-fs/ceph-client/lib/check_signature.c

## Purpose

`sources/distributed-fs/ceph-client/lib/check_signature.c` compares an MMIO region against a byte signature, typically for firmware or BIOS signature discovery.

## Important APIs, Types, and Functions

The exported API is `check_signature(const volatile void __iomem *io_addr, const unsigned char *signature, int length)`.

## Control Flow

The function loops for `length` bytes, reads each MMIO byte with `readb()`, compares it to the current signature byte, returns 0 on the first mismatch, and returns 1 after all bytes match.

## State and Persistence Behavior

There is no owned state. The function only performs ordered MMIO reads through the caller-provided mapping.

## Dependencies and Integration Points

Dependencies are `linux/io.h` and `linux/export.h`. Callers must obtain a valid `ioremap()` mapping and pass an appropriate signature buffer.

## Risks and Edge Cases

The length is signed; negative values skip the loop and return 1, so callers must validate length. MMIO side effects depend on the target region. The function assumes byte-wise reads are acceptable for the hardware.

## Test Signals

Tests should cover exact match, first/middle/last mismatch, zero length, caller-side validation of negative lengths, and use against mocked or safely mapped IO memory.

## Read Coverage

Source read size: 27 lines, 635 bytes.
