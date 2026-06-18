# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ntfs.c

## Scope

Implements NTFS detection, validation, label extraction, UUID formatting, and the internal `blkid_probe_is_ntfs()` helper.

## Behavior

- Defines NTFS boot sector/BPB, MFT record, and resident attribute layouts.
- `__probe_ntfs()` validates sector size, cluster encoding, maximum cluster size, required-zero BPB fields, MFT record size encoding, MFT cluster bounds, and the first MFT record magic.
- Reads `$Volume` MFT record and scans resident attributes for `MFT_RECORD_ATTR_VOLUME_NAME`, converting UTF-16LE label to UTF-8.
- Exports filesystem block size, logical sector block size, filesystem size, and volume serial UUID.
- `blkid_probe_is_ntfs()` runs the same validations without saving label/UUID, for collision checks elsewhere.

## Dependencies And Risks

- Relies on safe buffer reads at calculated MFT offsets and guarded attribute length/offset checks.
- Rejects plausible-looking boot sectors unless the MFT can be read and starts with `FILE`.
- MFT size arithmetic must remain bounded because it controls direct device reads.
