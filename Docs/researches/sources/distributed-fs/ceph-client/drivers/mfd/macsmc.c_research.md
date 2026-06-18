# sources/distributed-fs/ceph-client/drivers/mfd/macsmc.c

Purpose: this platform MFD driver is the Apple Silicon SMC core. It talks to SMC firmware through Apple RTKit, exports SMC key read/write APIs, manages notification delivery, and registers input, power, GPIO, hwmon, reboot, and RTC children.

Important APIs, types, and functions: `apple_smc_cmd_locked()` formats mailbox messages with command, size, write size, sequence ID, and data fields, sends them via `apple_rtkit_send_message()`, waits for completion, validates sequence/result, and returns response size/data. `apple_smc_rw_locked()` handles read/write/RW key transactions and SRAM shared-memory transfers. Exported APIs include `apple_smc_read()`, `apple_smc_write()`, `apple_smc_rw()`, `apple_smc_get_key_by_index()`, `apple_smc_get_key_info()`, `apple_smc_enter_atomic()`, and `apple_smc_write_atomic()`. RTKit callbacks handle crash, shared-memory setup, early replies, and notifications.

Control flow: probe maps the SRAM resource, initializes RTKit, wakes firmware, starts endpoint `0x20`, sends initialize, waits for boot shared-memory reply, reads key count, enables notifications, and registers child cells. Normal commands use `smc->mutex` and completions. Atomic shutdown writes use a spinlock, RTKit polling, and a pending flag.

State and persistence: `struct apple_smc` stores RTKit handle, SRAM mapping, shared-memory descriptor, boot stage, key count, sequence ID, completions, notifier chain, mutex/spinlock state, and atomic-mode flags. Hardware state includes SMC key values and notification enable key `NTAP`.

Dependencies and integration points: Apple RTKit, platform resources, OF compatible `"apple,t8103-smc"`/`"apple,smc"`, MFD core, blocking notifier chain, exported SMC key API for child drivers, and SRAM shared memory validation.

Risks: protocol sequencing is strict; missed completions or ID mismatch cause I/O failure. Atomic mode intentionally disables notifications and rejects normal commands. Shared-memory bounds checking must remain correct to avoid invalid SRAM access. Tests should cover boot timeout, RTKit crash, read/write small-vs-large payloads, key info decoding, notification fan-out, atomic write path, and child registration after key-count read.
