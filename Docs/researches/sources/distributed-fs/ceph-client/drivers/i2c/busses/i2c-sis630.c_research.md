# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-sis630.c

Purpose: Legacy SiS630/730/760/964 SMBus driver. It registers a singleton SMBus adapter after locating compatible SiS host hardware, enabling ACPI access, deriving the SMBus IO base, and reserving the IO register range.

Important APIs/types/functions: global `smbus_base` is the active IO base. Module parameters are `high_clock` and `force`. Register helpers are `sis630_read()`/`sis630_write()`. Transactions are split into `sis630_transaction_start()`, `sis630_transaction_wait()`, `sis630_transaction_end()`, and `sis630_transaction()`. `sis630_block_data()` handles multi-stage block reads/writes. `sis630_access()` maps Linux SMBus sizes to hardware protocol constants. `sis630_setup()`, probe, and remove manage PCI/IO integration.

Control flow: setup checks for supported SiS devices or force mode, enables ACPI through PCI BIOS control, reads ACPI base, chooses offset 0xE0 for SiS760 and 0x80 otherwise, checks ACPI conflicts, and reserves 20 IO ports. A transfer writes address/command/data/count registers, then runs transaction. Transaction start kills any busy transaction, saves old clock, optionally selects high clock, clears status, and starts the command. Wait polls status/error/collision/byte-done for block mode. End clears sticky status and restores clock. Block transfer streams data in 8-byte windows using `BYTE_DONE_STS`.

State and persistence: singleton static adapter and `smbus_base` persist while bound. `high_clock` temporarily changes host clock and restores it from `oldclock`; `force` bypasses detection. No IRQs or PM state are used.

Dependencies/integration: PCI, ACPI region checks, IO ports, I2C SMBus algorithm, HWMON class, and module PCI driver lifecycle.

Risks: singleton only. Force mode may operate on unsupported hardware. Block transfer logic is complex and depends on sticky byte-done clearing between 8-byte windows. The supported-chip scan uses global PCI search independent of the probed device. Clock changes are global to the SMBus controller. Timeout and collision recovery are limited.

Test signals: supported-device detection, force mode, SiS760 offset selection, ACPI conflict, high_clock restore, quick/byte/byte-data/word/process-call/block transfers, block lengths over 32 clamping, busy kill failure, timeout, collision `-EAGAIN`, device error `-ENXIO`, probe/remove cleanup.
