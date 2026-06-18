# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/exfat.c

exFAT detector and MBR collision helper. It validates the boot sector signature, jump code, `EXFAT   ` name, zeroed legacy BPB area, FAT count, sector/cluster shifts, FAT and cluster heap ranges, root directory cluster, and the required boot checksum over the first 11 sectors against all repeated checksum words in sector 12.

The probe walks the root directory cluster chain through the FAT to find a volume label entry, bounded by a 256 MiB directory scan cap. It emits the UTF-16LE label, serial-number UUID, filesystem revision, block size, and filesystem size. `blkid_probe_is_exfat` lets the DOS partition parser distinguish exFAT from vFAT-like boot sectors.

Risk is mainly in boot-sector arithmetic and FAT chain traversal; the code clamps shift ranges and cluster bounds before using computed offsets.
