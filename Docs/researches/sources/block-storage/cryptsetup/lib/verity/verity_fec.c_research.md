# File Research: sources/block-storage/cryptsetup/lib/verity/verity_fec.c

## Purpose
Implements dm-verity Forward Error Correction generation and verification/repair using Reed-Solomon codes.

## Key Responsibilities
- Validates FEC block-size and parity-root constraints.
- Computes interleaved RS byte offsets across protected input devices.
- Reads protected data and hash-area bytes into RS blocks.
- Encodes parity bytes to the FEC device or decodes parity for repair checking.
- Counts detected/corrected errors when requested.
- Computes the number of blocks covered by FEC and the number of RS parity blocks needed.

## Important Details
- FEC covers protected data plus hash area and optional padding/foreign metadata.
- If hash and FEC are the same device, coverage ends at `fec_area_offset`.
- If FEC is separate, coverage includes the hash device from hash offset to device end.
- FEC requires equal data and hash block sizes.
- RS parameters are 255-symbol blocks with roots constrained by min/max data symbol counts.

## Dependencies
Uses `verity.h`, `internal.h`, `rs.h`, device sizing/path helpers, and exact read/write buffer helpers.
