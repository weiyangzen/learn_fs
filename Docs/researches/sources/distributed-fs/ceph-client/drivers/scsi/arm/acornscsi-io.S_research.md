# sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi-io.S

## Purpose
`acornscsi-io.S` provides low-level ARM assembly block transfer routines for the Acorn SCSI card. It converts between the card's memory-mapped data presentation and normal byte streams in system memory, optimized for 16-, 8-, 4-, and 2-byte tails.

## Important APIs and routines
- `ENTRY(__acornscsi_in)`: prototype comment says `void acornscsi_in(unsigned int addr_start, char *buffer, int length)`. It reads from the SCSI card address in `r0` into the destination buffer in `r1` for `r2` bytes.
- `ENTRY(__acornscsi_out)`: prototype comment appears to repeat `acornscsi_in`, but the routine writes from memory buffer `r1` to card address `r0` for `r2` bytes.
- `LOADREGS` abstracts APCS-32 vs APCS-26 return register restoration, using `ldm...` with `^` for 26-bit APCS.

## Control flow and data transformation
Both routines align the card address down to a word boundary with `bic r0, r0, #3`. The input path loads words from the card, masks low 16-bit data using `0xffff`, combines pairs into normal 32-bit words, and stores to the destination buffer. It loops in 16-byte chunks, then handles 8-byte, 4-byte, and 1/2-byte residual cases. The output path performs the inverse transformation: it loads normal 32-bit words from memory, duplicates/shifts halfwords into the form expected by the card, stores them to the memory-mapped address, and then handles smaller residual lengths.

## State and persistence behavior
The routines are stateless aside from register saves/restores and the direct memory side effects of reading or writing the device-mapped address range and system buffer. They do not allocate memory, sleep, or maintain persistent data.

## Dependencies and integration points
The file depends on ARM assembler conventions, `<linux/linkage.h>`, `<asm/assembler.h>`, and Acorn machine hardware definitions. It is linked into `acornscsi_mod.o` by `drivers/scsi/arm/Makefile` and is called by the Acorn SCSI C driver for PIO-style data transfers.

## Risks and edge cases
- The routines assume ARM mode/register ABI and Acorn-specific bus layout; they are not portable across architectures.
- Address alignment is forced downward, so callers must pass an address compatible with the card's data window semantics.
- Residual handling uses condition flags from arithmetic on `r2`; off-by-one length bugs would corrupt trailing bytes.
- The input path uses low 16-bit masking, and the output path mirrors halfwords into words; any hardware change in data-lane layout would require assembly changes.
- The comment above `__acornscsi_out` names `acornscsi_in`, likely a copy/paste documentation error.

## Test signals
- Build should assemble this file for the intended ARM/APCS configuration.
- Functional testing should transfer buffers of lengths covering 0/1/2/3/4/8/16 and non-multiple tails, verifying byte-exact round trips where hardware permits.
- Runtime stress should cover unaligned card-window starts, high transfer lengths, and integration with the Acorn SCSI command data phase.
