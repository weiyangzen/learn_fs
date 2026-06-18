# sources/cloud-native/composefs/tools/composefs-dump.c

## Purpose
`composefs-dump.c` converts an existing composefs image into another EROFS-format composefs image. It is a small utility around libcomposefs read/write APIs, useful for dumping or normalizing image contents through the library node model.

## Important APIs, Types, And Functions
`usage` prints the `SRC DEST` contract. `write_cb` adapts `FILE *` output to `lcfs_write_options_s.file_write_cb`. `main` uses `lcfs_version_from_fd`, `lcfs_load_node_from_fd`, and `lcfs_write_to` with `LCFS_FORMAT_EROFS`.

## Control Flow
The program validates two positional arguments, opens the source read-only, reads the image version, loads the root `lcfs_node_s`, closes the input fd, opens the destination with `fopen(..., "we")`, and writes the loaded tree back out using the same version. On any open/load/write failure it exits through `err`/`errx`.

## State And Persistence
The only persistent output is the destination image. In-memory state is a loaded libcomposefs node tree that is unreferenced before exit. There is no incremental state or configuration file.

## Dependencies And Integration Points
It depends on `libcomposefs/lcfs-writer.h` and utility helpers. It integrates with images accepted by libcomposefs readers and with downstream consumers of generated EROFS composefs images.

## Risks
The utility does no option parsing beyond argument count and inherits all validation behavior from libcomposefs. Destination writes are direct to the requested path; interrupted writes may leave a partial output file. It preserves the detected version but does not expose min/max version controls.

## Test Signals
Round-trip tests should load an image, dump it, and compare structural output with `composefs-info dump` or remount behavior. Error tests should cover missing arguments, invalid source images, and unwritable destinations.
