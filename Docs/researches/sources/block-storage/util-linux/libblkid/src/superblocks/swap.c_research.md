# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/swap.c

## Scope

Implements Linux swap and suspend-image probing.

## Behavior

- Supports swap v0 (`SWAP-SPACE`), swap v1 (`SWAPSPACE2`), and suspend signatures including TuxOnIce and kernel hibernation variants.
- Rejects normal swap detection when TuxOnIce magic is present at the beginning of the device.
- For swap v1, validates version in either endian and nonzero last page, exports endianness, page-sized fs block size, filesystem size, and last block.
- Exports label and UUID when padding sanity suggests the v1 header region is valid.
- Registers signature offsets for several possible page sizes.

## Dependencies And Risks

- Page size is inferred from signature offset plus signature length.
- Endianness is derived from the version field.
- Suspend probing reuses swap header metadata but exports suspend-specific versions.
