# File Research: sources/block-storage/mdadm/Examine.c

## Purpose
`Examine.c` implements mdadm metadata examination for component devices and bad-block logs. It reads RAID superblocks or containers and prints detailed, brief, or export-formatted metadata without assembling arrays.

## Major Entry Points
- `Examine(struct mddev_dev *devlist, struct context *c, struct supertype *forcest)`
- `ExamineBadblocks(char *devname, int brief, struct supertype *forcest)`

## Examine Behavior
For each listed device, `Examine()` opens it read-only, chooses a metadata handler from a forced supertype, container detection, or superblock guessing, then attempts to load either an ordinary superblock or container metadata. Hardware compatibility checks are temporarily ignored during load.

If `--brief` is active, devices are grouped by array using metadata type and `compare_super()`. The code tracks devices in a linked-list helper, counts spares for non-container arrays, and later emits one brief mdadm.conf-style line per discovered array, optionally including devices and subarrays in verbose mode.

If `--export` is active, it calls metadata-specific `export_examine_super()` when available. Otherwise it prints the device name followed by metadata-specific detailed examination output. Each loaded superblock is freed after use unless retained for brief grouping.

## Bad-Block Examination
`ExamineBadblocks()` opens one device, guesses or uses forced metadata, verifies that the metadata format supports `examine_badblocks`, loads the superblock, and dispatches to the metadata handler. It reports missing metadata or unsupported bad-block examination as errors.

## Dependencies and Integration Points
This file is primarily a dispatcher into supertype callbacks: `load_super`, `load_container`, `getinfo_super`, `compare_super`, `brief_examine_super`, `brief_examine_subarrays`, `export_examine_super`, `examine_super`, and `examine_badblocks`.

## Safety and Risk Notes
The operations are read-only except for the optional SPARC adjustment path, which calls `update_super(..., UOPT_SPARC22, ...)` on loaded metadata state before printing. Error reporting is suppressed in scan/brief cases to support broad probing.
