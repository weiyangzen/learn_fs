# File Research: sources/block-storage/parted/libparted/labels/atari.c

Purpose: Full Atari partition-table backend supporting AHDI, ICD, and XGM-style extended/logical layouts.

Main interfaces: Registers `PedDiskType` named `atari` with extended-partition support. Implements probe, alloc, duplicate, free, read, clobber, write, partition allocation/duplication/destruction, system mapping, boot flag handling, alignment, numbering, metadata allocation, and partition limit reporting.

Control flow: `atari_probe()` validates a magic-less format by reading the root sector, checking disk size and bad-sector-list fields, validating AHDI primary entries, rejecting invalid/multiple/slot-zero XGM layouts, walking XGM auxiliary root sectors, and optionally validating ICD entries. `atari_read()` parses AHDI primaries, XGM logical chains, or ICD entries into `PedPartition`s. `atari_write()` preserves bootability, fixes stored device size when requested, fills AHDI/ICD entries, writes XGM ARS sectors, writes the root sector, and initializes an HDX-compatible bad-sector list if needed.

Data model: `AtariRawTable` is exactly one 512-byte sector containing boot code, ICD entries, disk size, four AHDI entries, BSL fields, and checksum. `AtariDisk` tracks current mode, BSL location, and whether content has been read/written. `AtariPart` tracks 3-character Atari and ICD partition IDs plus boot flags.

Important details and risks: The backend has complex numbering rules: XGM extended partitions use libparted number 0, logical partitions may force renumbering of following primaries, and ICD mode is incompatible with XGM. Bootability is represented by a root-sector checksum, with safeguards against DOS-like forbidden signatures for non-boot sectors. Alignment avoids the bad-sector-list range and reserves ARS metadata sectors before logical partitions. Tests should cover empty signed labels, AHDI-only layouts, ICD overflow primaries, XGM logical chains, BSL conflicts, boot checksum preservation, partition ID mapping, and max-partition limits.
