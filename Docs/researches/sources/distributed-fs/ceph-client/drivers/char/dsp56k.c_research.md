# sources/distributed-fs/ceph-client/drivers/char/dsp56k.c

## Purpose
This is the Atari DSP56001 character driver. It exposes the Atari DSP host port at major `DSP56K_MAJOR`, supports upload of DSP programs via firmware-assisted bootstrap, and moves data between userspace and the DSP in 8-, 16-, 24-, or 32-bit word sizes.

## Important APIs, Types, and Functions
- Hardware access is through `dsp56k_host_interface` and Atari `sound_ym` registers.
- `struct dsp56k_device` tracks open state, max I/O burst, timeout, and selected TX/RX word sizes.
- `dsp56k_upload()` resets the DSP, loads `dsp56k/bootstrap.bin`, streams user program words, and sends the execute command.
- `dsp56k_read()` and `dsp56k_write()` use `handshake`, `tx_wait`, and `rx_wait` macros around host-port readiness bits.
- `dsp56k_ioctl()` handles `DSP56K_UPLOAD`, word-size changes, host flags, and host command writes.

## Control Flow
Module init checks Atari hardware presence, registers the char device and class device, then leaves the DSP idle. `open()` enforces exclusive use with a bit flag, resets per-open defaults, disables DSP host interrupts, and clears host flags. Reads and writes dispatch on minor 0 and the selected word size, waiting for receive/transmit readiness before copying each item. Upload reset powers the DSP down/up, writes bootstrap firmware as 24-bit words, then streams the caller's binary.

## State and Persistence Behavior
Runtime state is global and protected by `dsp56k_mutex` for open/ioctl state changes and upload. The actual DSP program persists in DSP memory until reset or power state changes. Word-size settings are per global device, reset on open, not per file descriptor beyond exclusive access.

## Dependencies and Integration Points
The driver depends on m68k Atari platform headers, firmware loader support, a platform device used only as firmware-loading context, and `asm/dsp56k.h` ioctl definitions. Userspace integrates through `/dev/dsp56k`, ioctl commands, and binary firmware `dsp56k/bootstrap.bin`.

## Risks
The `handshake` macro embeds user copies and returns from the caller, making error paths hard to audit. Some `get_user()`/`put_user()` calls inside handshake do not inspect individual copy return values. The firmware load path registers a temporary platform device and assumes the bootstrap image size is a multiple of three bytes.

## Test Signals
Compile for Atari with DSP56K present. Test exclusive open, invalid minor handling, ioctl argument validation, missing and malformed bootstrap firmware, all TX/RX word sizes, and nonblocking expectations at userspace level through controlled host-port readiness.
