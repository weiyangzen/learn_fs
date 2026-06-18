# sources/distributed-fs/ceph-client/include/linux/platform_data/cros_ec_chardev.h

Purpose: defines the ChromeOS EC character-device userspace ABI for sending EC commands, reading mapped EC memory, and configuring event masks.

Important APIs and types: `CROS_EC_DEV_VERSION` identifies ABI version. `struct cros_ec_readmem` contains memory-map `offset`, requested `bytes`, and a fixed `buffer[EC_MEMMAP_SIZE]`; zero bytes means read a NUL-terminated string up to the EC memory-map limit. Ioctls use `CROS_EC_DEV_IOC`: `CROS_EC_DEV_IOCXCMD` transfers `struct cros_ec_command`, `CROS_EC_DEV_IOCRDMEM` transfers `struct cros_ec_readmem`, and `CROS_EC_DEV_IOCEVENTMASK` manages event masks.

Control flow: userspace opens the EC chardev and issues ioctls. The driver copies command/readmem structs from userspace, validates offsets and lengths, talks to the EC transport/LPC memory map, copies results back, and reports byte counts or errors.

State and persistence: ABI structs are per-ioctl data. Runtime state includes EC device transport, event masks, and mapped memory contents; persistent EC settings are managed by firmware/commands outside this header.

Dependencies and integration points: depends on bits, ioctl, types, and `linux/platform_data/cros_ec_commands.h`. Integrates userspace tools, ChromeOS EC command protocol, LPC/transport-specific EC drivers, and event handling.

Risks and test signals: risks include ABI layout changes, insufficient bounds checks on `offset`/`bytes`, command size validation bugs, event mask compatibility, and 32/64-bit ioctl issues. Test ioctl command round trips, mapped memory reads including zero-length string mode, invalid offset/length, compat userspace, event mask operations, and EC transport failure paths.
