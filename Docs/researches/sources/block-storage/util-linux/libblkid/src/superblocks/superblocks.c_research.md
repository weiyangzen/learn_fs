# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/superblocks.c

## Scope

Implements the central libblkid superblock probing chain, supported idinfo ordering, safe-probe ambiguity handling, filters, and superblock result setters.

## Behavior

- Defines ordered `idinfos[]`: OPAL/LUKS and RAID/container formats first, then filesystems, with comments and ordering used to avoid unsafe reads and misclassification.
- `superblocks_probe()` iterates idinfos, applies filters, minimum size checks, CD/floppy exclusions, magic matching, optional probefunc validation, then exports `TYPE`, `USAGE`, and `SBMAGIC`.
- `superblocks_safeprobe()` repeatedly probes to detect multiple matches, returns the first tiny-device result, stops at RAID/crypto, and reports `BLKID_PROBE_AMBIGUOUS` when multiple intolerant filesystem signatures exist.
- Public APIs enable/disable superblock probing, configure flags, reset/invert filters, filter by type or usage, enumerate known names, and test known filesystems.
- Setter helpers gate exported fields by flags: version, usage, label/raw label, UUID/raw UUID, size, last block, fs block size, minimal block size, and endianness.

## Dependencies And Risks

- Correct idinfo ordering is a core invariant; moving probes can change collision behavior.
- Probe functions must clear partial values on failed validation, which this driver does via chain reset.
- Safe probing intentionally does not search past the first RAID/crypto result for filesystem collisions.
- Label/UUID setters trim whitespace and suppress empty values, while raw variants preserve original data when requested.
