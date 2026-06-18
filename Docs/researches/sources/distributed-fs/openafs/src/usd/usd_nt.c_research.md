
# sources/distributed-fs/openafs/src/usd/usd_nt.c

`usd_nt.c` is the WinNT implementation of the USD abstraction. It wraps Win32 `HANDLE`s, maps Unix-style errno returns through `nterr_nt2unix`, handles regular files, disk devices, and tape drives, and implements tape operations with Win32 tape APIs.

Important functions are `usd_DeviceRead`, `usd_DeviceWrite`, `usd_DeviceSeek`, `usd_DeviceIoctl`, `usd_DeviceClose`, `usd_DeviceOpen`, `usd_Open`, `usd_StandardInput`, and `usd_StandardOutput`. Open maps USD flags to `CreateFile` access/share/create/attribute flags; read/write call `ReadFile` and `WriteFile`; seek maps whence to `SetFilePointerEx` and optionally bounds disk-device offsets using cached geometry-derived size in `privateData`.

`usd_DeviceIoctl` detects object type using `GetFileInformationByHandle`, `IOCTL_DISK_GET_DRIVE_GEOMETRY`, and `GetTapeStatus`; supports size get/set, full name, block size, seekability, and tape commands. Tape operations map to `WriteTapemark`, `SetTapePosition`, `PrepareTape`, `GetTapeStatus`, and `GetTapeParameters`, with retries for transient media/bus errors during prepare/rewind flows.

Persistence is through Win32 file/device handles. `USD_OPEN_SYNC` maps to `FILE_FLAG_WRITE_THROUGH`; locks are approximated through sharing modes because Windows locks devices by handle. `USD_IOCTL_SETSIZE` seeks then calls `SetEndOfFile`. Close frees `fullPathName` and the USD handle after `CloseHandle`.

Risks include privateData storing a 32-bit kilobyte upper bound in a pointer, coarse disk size estimation from whole-disk geometry, `USD_IOCTL_GETDEV` unreachable code after an immediate `EINVAL`, standard input/output helpers allocating handles but not assigning `*usdP`, and platform-specific tape behavior. Test signals include regular file and device open modes, share-lock conflicts, disk seek bounds, tape prepare/rewind transient retries, end-of-media write behavior, and standard stream wrapper correctness.
