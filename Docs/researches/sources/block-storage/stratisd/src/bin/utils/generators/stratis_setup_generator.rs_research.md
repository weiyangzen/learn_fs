# File Research: sources/block-storage/stratisd/src/bin/utils/generators/stratis_setup_generator.rs

Systemd generator for Stratis root filesystem setup in initrd.

Key behavior:
- Reads `stratis.rootfs.pool_uuid` from `/proc/cmdline`.
- If missing, logs a warning and exits successfully.
- Parses the pool UUID.
- Writes `stratis-setup.service` into the early generator directory.
- Creates `/run/systemd/system/initrd.target.wants` if needed and symlinks the generated unit into it.
- Generated unit wants `stratisd-min.service`, console ask-password, and Clevis setup, then runs `/usr/lib/systemd/stratis-rootfs-setup`.

Filesystem relevance:
- Boot-time bridge for activating a Stratis-managed root filesystem.
