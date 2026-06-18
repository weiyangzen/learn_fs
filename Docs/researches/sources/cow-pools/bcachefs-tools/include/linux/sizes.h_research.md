# File Research: sources/cow-pools/bcachefs-tools/include/linux/sizes.h

Defines standard Linux `SZ_*` byte-size constants from 1 byte through 64 TiB, using `_AC(..., ULL)` where values exceed 32-bit range. It is pure macro compatibility.
