
# sources/distributed-fs/openafs/src/usd/usd.h

`usd.h` defines the public user-space device abstraction used by OpenAFS components that need to treat regular files and devices uniformly across Unix and Windows. It exposes an opaque-ish `usd_handle_t` containing operation function pointers plus private handle fields.

Important APIs are `usd_Open`, `usd_StandardInput`, `usd_StandardOutput`, and macros `USD_READ`, `USD_WRITE`, `USD_SEEK`, `USD_IOCTL`, and `USD_CLOSE`. Open flags include read-only/read-write, synchronous I/O, read/write lock, and create. Ioctls include type, full name, device id, size get/set, tape operation, block size, and seekability. Tape operations include write EOF, rewind, forward/backward space file, prepare, and shutdown.

State is held in `struct usd_handle`: callbacks, platform handle, full path, open flags, and private data. The header documents errno-style integer returns and output parameters for transferred byte counts and offsets. It also documents the Windows constraint that device locks must be tied to open handles.

Dependencies are AFS integer types and platform implementations in `usd_file.c`/`usd_nt.c`. Risks include callers treating private fields as stable, the macro API lacking null checks, and cross-platform semantic gaps for devices, locks, and seekability. Test signals are compile coverage and exercising all ioctl cases through `usd_test` and regular-file unit tests.
