# File Research: sources/block-storage/parted/libparted/fs/hfs/probe.h

Declaration header for HFS probe helpers. It includes libparted, endian/debug, and `hfs.h`, then declares sector-size validation and probe entry points: `hfsc_can_use_geom()`, `hfs_and_wrapper_probe()`, `hfsplus_probe()`, `hfs_probe()`, and `hfsx_probe()`.

The functions are consumed by `hfs.c` for filesystem type registration and may be reused by HFS resize code that needs wrapper detection.
