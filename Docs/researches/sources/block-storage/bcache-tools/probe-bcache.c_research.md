# File Research: sources/block-storage/bcache-tools/probe-bcache.c

`probe-bcache` is a blkid fallback scanner. It accepts `-o udev`, skips devices that blkid already recognizes, reads the bcache superblock at `SB_START`, verifies magic, and prints either udev environment lines or a blkid-like output line.

For udev it emits `ID_FS_UUID`, `ID_FS_UUID_ENC`, and `ID_FS_TYPE=bcache`, allowing `69-bcache.rules` to register devices even on systems whose blkid lacks bcache support.
