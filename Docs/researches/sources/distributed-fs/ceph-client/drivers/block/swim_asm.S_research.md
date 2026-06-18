# sources/distributed-fs/ceph-client/drivers/block/swim_asm.S

## Purpose
Provides timing-sensitive m68k assembly helpers for the original SWIM floppy driver. These routines read MFM sector address headers and sector data directly from SWIM registers.

## Important APIs, types, and functions
- Exports `swim_read_sector_header(struct swim __iomem *base, struct sector_header *header)`.
- Exports `swim_read_sector_data(struct swim __iomem *base, unsigned char *data)`.
- Internal routines `mfm_read_addrmark` and `mfm_read_data` wait for address/data marks, read bytes, and return either bytes read or `-1`.
- Constants define SWIM register offsets, sector header field offsets, seek/retry loop limits, and 512 byte sector size.

## Control flow
The C driver calls the exported functions with interrupts disabled around repeated sector scanning. The assembly resets selected mode registers, waits for MFM address marks (`a1 a1 a1 fe`) or data marks (`a1 a1 a1 fb`), copies header fields or data bytes into the caller buffer, reads trailing CRC bytes, clears mode, and returns.

## State and persistence behavior
No persistent state is kept. The routines manipulate hardware registers and caller-provided buffers. Return value `512` indicates a full data sector read; `-1` indicates timeout or missing expected byte; header read returns `0` on its normal exit.

## Dependencies and integration points
Architecture-specific to m68k Macintosh SWIM hardware. It is linked with `swim.c`, which declares the extern functions and interprets returned data while managing higher-level geometry and retries.

## Risks and test signals
- Correctness depends on exact polling loops and instruction timing; compiler-level C rewrites would be risky.
- Header path appears to set `d0 = 0` on `header_exit` after possible timeout through `bpl header_exit`, so caller validation of header fields is important.
- Hardware tests should include marginal disks, CRC errors, missing address marks, short reads, and repeated retries while validating no register mode is left active after failures.
