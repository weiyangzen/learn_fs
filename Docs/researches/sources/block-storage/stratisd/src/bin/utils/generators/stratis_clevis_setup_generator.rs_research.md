# File Research: sources/block-storage/stratisd/src/bin/utils/generators/stratis_clevis_setup_generator.rs

Systemd generator for Clevis setup of a Stratis root filesystem.

Key behavior:
- Reads `stratis.rootfs.pool_uuid` from `/proc/cmdline`.
- If missing, logs a warning and disables itself without error.
- Parses the pool UUID.
- Writes `stratis-clevis-setup.service` into the early generator directory.
- The generated unit wants/starts `stratisd-min.service` and `network-online.target`, runs `/usr/lib/systemd/stratis-clevis-rootfs-setup`, and exports `STRATIS_ROOTFS_UUID`.

Error handling:
- `generator()` sets up systemd logging, runs the generator, logs failures, and returns the original result.
