# sources/distributed-fs/ceph-client/arch/parisc/kernel/pdc_cons.c

Purpose: provides early console output through PA-RISC PDC/IODC firmware before a normal console driver is available, with optional KGDB polling input.

Important functions and state are `pdc_console_write`, optional `kgdb_pdc_read_char`, `kgdb_pdc_write_char`, `kgdb_pdc_io_ops`, `pdc_earlycon_setup`, and `EARLYCON_DECLARE(pdc, ...)`. It uses `PAGE0->mem_cons` and `PAGE0->mem_kbd` firmware console descriptors and the PDC helpers `pdc_iodc_print` and `pdc_iodc_getc`.

Control flow is simple but early-boot sensitive. Earlycon setup checks whether the firmware console is duplex; if so, it copies console output parameters into the keyboard/input descriptor so reads and writes use the same device. It installs `pdc_console_write` as the console write callback and marks the port as big-endian memory-mapped I/O. When KGDB is configured it registers `kgdb_pdc` read/write operations. Writes loop until `pdc_iodc_print` reports the full byte count has been emitted.

State is firmware console descriptor data in page zero, the early console object, optional KGDB I/O registration, and no persistent kernel buffers. Dependencies are early console infrastructure, serial core constants, KGDB, page-zero firmware data, and PDC IODC routines.

Risks include infinite write looping if firmware reports no progress, reliance on firmware calls before full kernel services exist, duplex descriptor assumptions, no-op KGDB writes because normal console already echoes output, and very slow firmware I/O changing boot timing. Test signals are early boot messages with `earlycon=pdc`, KGDB character polling on supported firmware, no crash before console handoff, and correct output on both serial and graphics/firmware console configurations.
