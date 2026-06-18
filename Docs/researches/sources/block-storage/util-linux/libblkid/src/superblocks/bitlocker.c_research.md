# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bitlocker.c

BitLocker detector and collision helper. It recognizes Vista, Windows 7, and BitLocker To Go boot signatures, then for newer formats follows the metadata offset to the FVE metadata header and validates the `-FVE-FS-` block signature. `blkid_probe_is_bitlocker` exposes this logic so NTFS/vFAT probes can avoid misidentifying encrypted volumes.

The main probe reports `BitLocker` with crypto usage. When FVE metadata is available it sets the metadata version, scans metadata entries for a UTF-16LE description label, and formats the volume identifier using Microsoft GUID byte ordering.

The implementation bounds metadata entry walking by the declared metadata size and checks entry alignment/size before use. Vista detection can succeed from the boot signature alone and therefore has less metadata output than Win7/To Go.
