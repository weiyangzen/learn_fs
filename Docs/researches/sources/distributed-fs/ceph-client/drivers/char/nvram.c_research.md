# sources/distributed-fs/ceph-client/drivers/char/nvram.c

## Purpose
`nvram.c` implements `/dev/nvram` as a misc device for CMOS/NVRAM access. On x86 it provides the backing `arch_nvram_ops` for MC146818 RTC CMOS bytes, including checksum validation and repair. It also provides architecture-specific ioctls for PC/M68K checksum operations and PPC partition/sync operations.

## Important APIs, Types, and Functions
- x86 low-level helpers `pc_nvram_read_byte()`, `pc_nvram_write_byte()`, `pc_nvram_read()`, `pc_nvram_write()`, `pc_nvram_get_size()`, `pc_nvram_set_checksum()`, and `pc_nvram_initialize()` implement `arch_nvram_ops`.
- `__nvram_check_checksum()` and `__nvram_set_checksum()` operate on PC bytes 2 through 31 and checksum bytes 32 and 33.
- `nvram_misc_read()` and `nvram_misc_write()` bound transfers by `nvram_size` and `PAGE_SIZE`, stage through kernel memory, and call the architecture NVRAM helpers.
- `nvram_misc_ioctl()` handles `NVRAM_INIT`, `NVRAM_SETCKS`, PPC `IOC_NVRAM_GET_OFFSET`, and PPC sync.
- `nvram_misc_open()` and `nvram_misc_release()` enforce exclusive open modes and single-writer rules when checksum updates are supported.
- x86 procfs support creates `/proc/driver/nvram` with decoded CMOS configuration fields.

## Control Flow
Module init obtains `nvram_size` through `nvram_get_size()`, registers the fixed-minor misc device `NVRAM_MINOR`, and optionally creates the procfs entry. Reads and writes validate the file position, cap the count, allocate a temporary buffer, and delegate to `nvram_read()` or `nvram_write()`. The x86 backend checks the checksum before every full read/write and rewrites the checksum after writes.

## State and Persistence
The driver exposes persistent nonvolatile storage. Software state tracks `nvram_open_cnt`, `nvram_open_mode`, and `nvram_size`. x86 access is serialized with the global `rtc_lock` because CMOS uses index/data ports shared with RTC code. Open-mode state is protected by `nvram_state_lock`; ioctl and architecture operations use `nvram_mutex` where needed.

## Dependencies and Integration Points
This file integrates with `linux/nvram.h`, architecture-provided `arch_nvram_ops`, RTC CMOS access, misc core, procfs/seq_file, PPC platform methods, and capability checks. It is both a user-facing char device and an exported architecture NVRAM service.

## Risks
- Incorrect writes can corrupt CMOS/NVRAM machine configuration; checksum enforcement reduces but does not remove that risk.
- `NVRAM_INIT` clears the whole available NVRAM area and is guarded only by `CAP_SYS_ADMIN`.
- Concurrent raw CMOS users outside this driver must obey `rtc_lock`.
- Open exclusivity is advisory within this misc device and does not protect external architecture users of `arch_nvram_ops`.

## Test Signals
Test signals include successful misc registration, correct `llseek` bounds, `-EIO` on bad checksum, `CAP_SYS_ADMIN` enforcement for checksum/init ioctls, single-writer `-EBUSY` behavior, and procfs output on x86. Architecture tests should use mocked or emulated `arch_nvram_ops` where possible to avoid destructive real CMOS writes.
