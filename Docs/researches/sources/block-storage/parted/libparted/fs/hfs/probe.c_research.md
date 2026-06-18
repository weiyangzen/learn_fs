# File Research: sources/block-storage/parted/libparted/fs/hfs/probe.c

HFS/HFS+/HFSX probe implementation. `hfsc_can_use_geom()` rejects devices whose sector size is not 512 bytes, because the code assumes classic HFS sector layout.

`hfs_and_wrapper_probe()` detects an HFS master directory block at byte offset 1024 and scans expected alternate MDB positions near the computed end of the volume. It returns a geometry sized to the detected HFS wrapper/base volume. `hfsplus_probe()` first checks for HFS+ embedded in an HFS wrapper by looking at the embedded signature in the wrapper MDB; if absent, it detects standalone HFS+ by reading the volume header at sector 2 and scanning alternate volume headers near the legal/legacy end ranges. `hfs_probe()` accepts plain HFS only when `hfs_and_wrapper_probe()` succeeds and `hfsplus_probe()` does not identify an embedded HFS+ volume. `hfsx_probe()` similarly validates HFSX signature and legal alternate volume header positions.

The probes return geometries sized by discovered alternate header positions, not merely input geometry. They validate signatures but do not parse B-trees or journal state.
