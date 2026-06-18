# File Research: sources/block-storage/vdo/utils/vdo/vdoformat.c

## Purpose

`vdoformat.c` implements `vdoformat`, the low-level formatter for VDO block devices. It validates the target block device, checks for existing signatures, prepares VDO and UDS index configuration, writes initial metadata through `formatVDO()`, verifies the formatted VDO, and prints capacity guidance.

## Command-Line Interface

Usage:

```text
vdoformat [options] filename
```

Options:

- `--force`
- `--help`
- `--logical-size=<size>`
- `--slab-bits=<bits>`
- `--uds-memory-size=<gigabytes>`
- `--uds-sparse`
- `--verbose`
- `--version`

Defaults:

- Logical size defaults inside formatting logic when `logicalSize == 0`.
- Slab bits default to `19`.

## Main Flow

`main()`:

1. Registers status codes.
2. Parses format parameters into `logicalSize`, `slabBits`, `UdsConfigStrings`, `verbose`, and `force`.
3. Requires exactly one target filename.
4. Stats the file and requires a block device.
5. Extracts major/minor and checks `/sys/dev/block/<major>:<minor>/holders` to ensure no active holders.
6. Opens the device read-write.
7. Uses `BLKGETSIZE64` to get physical byte size.
8. Rejects devices larger than `MAXIMUM_VDO_PHYSICAL_BLOCKS * VDO_BLOCK_SIZE`.
9. Closes the FD.
10. Builds `struct vdo_config`.
11. Validates logical size alignment and max logical block count.
12. Creates a `PhysicalLayer`.
13. Checks existing signatures using blkid, requiring `--force` if found.
14. Parses UDS index config.
15. Allocates a zero buffer and writes one block at block 1 to clear old UDS superblock state.
16. Calls `formatVDO(&config, &indexConfig, layer)`.
17. Handles common format errors with extra diagnostic help.
18. Loads the newly formatted VDO to verify it.
19. Prints capacity/growth information via `describeCapacity()`.
20. Frees VDO and destroys the layer.

## Existing Signature Detection

`checkForSignaturesUsingBlkid()`:

- Creates a blkid probe.
- Enables partition and superblock probing.
- Iterates detected signatures.
- Prints details using `printSignatureInfo()`.
- If signatures are found:
  - with `--force`: prints a warning and continues.
  - without `--force`: returns `EPERM`.

`printSignatureInfo()` reports offset, label, UUID, type, and usage where blkid exposes them.

## Device-In-Use Check

`checkDeviceInUse()` builds `/sys/dev/block/<major>:<minor>/holders` and counts entries using `countHolders()`.

It retries up to 25 times with 200 ms sleep, then fails if holders remain.

## Capacity Reporting

`describeCapacity()` prints:

- Whether logical blocks defaulted.
- Physical addressable size across current data slabs.
- Slab count and slab size.
- Maximum growable physical address space based on `MAX_VDO_SLABS`.
- Advice about choosing larger slabs when needed.

`printReadableSize()` handles human-ish B/KB/MB/GB/TB/PB display for these messages.

## Dependencies

Includes:

- System/library: `blkid/blkid.h`, `dirent.h`, `err.h`, `getopt.h`, `linux/fs.h`, `stdio.h`, `stdlib.h`, `unistd.h`, `sys/ioctl.h`, `sys/stat.h`, `sys/sysmacros.h`
- Utility: `errors.h`, `fileUtils.h`, `logger.h`, `string-utils.h`, `syscalls.h`, `time-utils.h`
- VDO/base: `constants.h`, `status-codes.h`, `types.h`, `vdoConfig.h`
- VDO helpers: `fileLayer.h`, `parseUtils.h`, `userVDO.h`, `vdoVolumeUtils.h`

## Notable Behaviors and Risks

- `optionString` includes an unused `i` option; there is no corresponding long option or switch case.
- `countHolders()` increments the caller’s holder count but does not reset it; `checkDeviceInUse()` calls it repeatedly with the same `holders` variable. If holders are present initially, this can accumulate counts across retries rather than observing a fresh count.
- The zero buffer allocated before clearing block 1 is not explicitly initialized in this file; correctness depends on the layer allocator returning zeroed memory or on external guarantees.
- The formatter only accepts block devices, not regular files.
- On `VDO_NO_SPACE`, it calculates and prints the minimum required VDO size.
