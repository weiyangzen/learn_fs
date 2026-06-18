# File Research: sources/block-storage/parted/libparted/fs/r/hfs/file.h

Declares classic HFS private file accessors.

Exports:
- Open/close for an HFS file fork from CNID and initial extents.
- Single-sector read/write.

Role:
- Used to access HFS special files such as extents and catalog files.
