# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/spk_ttyio.c

## Purpose
TTY line discipline transport for Speakup synthesizers, allowing normal tty devices such as `ttyS0` or `ttyUSB0` instead of direct UART stealing.

## Important APIs, Types, And Functions
`struct spk_ldisc_data` stores one received byte, completion, free flag, and synth pointer. Exports `spk_ttyio_ops`, ldisc register/unregister, synth probe/release, and immediate output. Static functions implement device lookup, ldisc open/close/receive, tty writes, UTF-8 output, modem control, input waits, and buffer flush.

## Control Flow
Probe resolves `dev` or `ser`, opens the tty exclusively, enables hardware flow control where possible, temporarily authorizes `N_SPEAKUP` install through `speakup_tty`, stores `synth->dev`, and marks alive. Receive callbacks either pass bytes to `read_buff_add` or complete a one-byte wait. Output uses `tty->ops->write`.

## State And Persistence Behavior
Global `speakup_tty` is protected by `speakup_tty_mutex`; per-tty state lives in `disc_data`; `synth->dev` holds the tty. The ldisc is registered at Speakup init and removed at exit.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on tty core, line disciplines, completions, termios, and synth descriptors. Risks are tty lifetime, unauthorized ldisc opens, single-byte receive drops, and write-error deactivation. Test invalid devices, exclusive open failures, flow-control setting, receive paths, Unicode output, write errors, and release cleanup.
