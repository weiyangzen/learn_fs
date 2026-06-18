# sources/distributed-fs/ceph-client/arch/m68k/atari/nvram.c

Purpose: Atari TT/Falcon-style NVRAM access and `/proc/driver/nvram` reporting.

Important APIs are `atari_nvram_read()`, `atari_nvram_write()`, `atari_nvram_get_size()`, `atari_nvram_initialize()`, and `atari_nvram_set_checksum()`. Internal helpers read/write bytes at `NVRAM_FIRST_BYTE` using CMOS RTC accessors and maintain the Atari checksum over bytes 0-47 with checksum bytes 48-49.

Control flow for reads and writes takes `rtc_lock`, verifies checksum, copies bytes within the fixed 50-byte NVRAM range, updates `*ppos`, and rewrites checksum after writes. Initialization zeroes all bytes and sets checksum. The proc reader snapshots contents under lock, reports checksum status, boot preference, SCSI arbitration/host ID, and Falcon language/date/video preferences.

State is persistent NVRAM/RTC CMOS storage, guarded by the global `rtc_lock` from `time.c`. No separate kernel cache is kept.

Dependencies include `mc146818rtc` CMOS macros, Atari hardware presence, procfs, seq_file, and RTC locking. Integration requires Atari with `TT_CLK`; the proc entry is registered at `device_initcall`.

Risks and test signals: all CMOS access must hold `rtc_lock`; checksum failure prevents reads/writes; proc display assumes a full valid snapshot. Test checksum initialize/set, bounded reads/writes with offsets, concurrent RTC/NVRAM access, and proc output on TT/Falcon configs.
