# sources/distributed-fs/ceph-client/arch/x86/boot/tty.c

Purpose: provides early text input/output via BIOS console and optional serial mirroring.

Important APIs and state: defines global `early_serial_base`; exports `putchar()`, `puts()`, `getchar()`, `kbd_flush()`, and `getchar_timeout()`. Local helpers write serial, write BIOS teletype, read CMOS seconds, and test keyboard pending.

Control flow: `putchar()` converts newline to CRLF, writes BIOS INT 10h teletype, and mirrors to serial if initialized. Keyboard timeout polls INT 16h and BIOS time for about 30 seconds.

Dependencies and integration: used for all setup diagnostics, video menu interaction, CPU/EDD messages, and early serial output. Depends on BIOS INT 10h/16h/1Ah and port I/O indirection.

Risks and test signals: BIOS calls are unavailable after protected mode, so use is confined to setup/inittext. Serial transmit waits with a bounded timeout. Test video menu input, timeout behavior, CRLF output, and serial mirroring with `earlyprintk`.
