# File Research: sources/block-storage/parted/libparted/fs/r/filesys.c

Generic libparted filesystem operation dispatch for the resizable filesystem subset.

Key behavior:
- Maps probed type names to open/close/resize/constraint functions for HFS, HFS+, HFSX, and FAT.
- `ped_file_system_open()` opens the device, probes the filesystem, validates probed geometry against the supplied geometry, dispatches to type-specific open, and attaches type.
- `ped_file_system_close()` dispatches close and closes the device.
- `ped_file_system_resize()` clobbers signatures in the target geometry outside the existing filesystem, then dispatches type-specific resize.
- `ped_file_system_get_resize_constraint()` dispatches type-specific constraint calculation.
- Static clobber helpers clear filesystem signatures at start/end while respecting an exclude geometry.

Important dependencies:
- FAT/HFS/HFS+ exported open/close/resize/constraint functions.
- `pt-tools.h` sector clearing.
- libparted probing and geometry APIs.

Notable constraints:
- Only the explicitly mapped filesystem families are supported by this resize frontend.
