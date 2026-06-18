# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/xfs.c

## Scope

Implements XFS filesystem probing and XFS external log detection.

## Behavior

- Defines the XFS superblock, converts big-endian disk fields into a CPU-order copy, and validates geometry beyond the `XFSB` magic.
- Checks sector size, block size, inode size, logs, realtime extent size, allocation group limits, inode percent, and total data blocks.
- For v5 superblocks, verifies required feature bits and CRC32C excluding the checksum field.
- Exports label, UUID, filesystem size excluding internal log blocks, last block count, filesystem block size, and sector block size.
- External log probing scans the first 256 KiB by 512-byte sectors, rejects regular XFS superblocks, validates log record headers, and exports `LOGUUID`.

## Dependencies And Risks

- XFS validation intentionally avoids trusting magic alone.
- External log detection requires minimum size and validates log format/version/body length.
- Filesystem size calculation depends on internal-vs-external log interpretation.
