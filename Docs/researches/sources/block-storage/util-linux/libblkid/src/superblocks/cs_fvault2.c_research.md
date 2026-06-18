# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/cs_fvault2.c

Apple Core Storage/FileVault2 physical-volume detector. It matches `CS` at the physical-volume header magic offset, requires version 1 and checksum algorithm 1, verifies a seeded CRC32C over the header after the checksum field, and then narrows detection to FileVault2-like block type `0x10`, 16-byte key data, and AES-XTS cipher id.

On success it reports `cs_fvault2`, crypto usage, version, and physical-volume UUID. The file deliberately does not derive filesystem size or block geometry because the actual filesystem lives above Core Storage/dm-crypt and would require parsing additional metadata blocks.
