# sources/distributed-fs/ceph-client/drivers/input/serio/serport.c

## Purpose
`serport.c` implements the `N_MOUSE` TTY line discipline named `input`, converting a serial TTY byte stream into a `SERIO_RS232` port. It lets serial input devices such as tablets and touchscreens bind to normal serio protocol drivers via tools like `inputattach`.

## Important APIs, types, and functions
`struct serport` stores the tty, waitqueue, active serio port, serio ID, spinlock, and flags `SERPORT_BUSY`, `SERPORT_ACTIVE`, and `SERPORT_DEAD`. The line discipline callbacks are open, close, read, ioctl, compat ioctl, receive buffer, hangup, and write wakeup. Serio callbacks implement write, open, and close.

## Control flow
Opening the line discipline requires `CAP_SYS_ADMIN`, allocates state, sets `receive_room`, and enables write wakeups. The read method is the long-lived activation path: it creates a serio port, fills name/phys/protocol/write/open/close fields, registers it, then sleeps until hangup marks the port dead. Incoming TTY bytes are ignored until the serio driver opens the port; then receive-buffer callbacks translate TTY parity/frame flags into `SERIO_PARITY` or `SERIO_FRAME` and call `serio_interrupt()`. `SPIOCSTYPE` sets protocol/id/extra before registration.

## State and persistence
State exists only while the line discipline is installed. The protocol selection in `serport->id` persists for that ldisc instance until close. `SERPORT_ACTIVE` follows serio open/close, `SERPORT_BUSY` prevents multiple concurrent readers from creating multiple ports, and hangup wakes the read path for orderly unregister.

## Dependencies and integration points
This file integrates the TTY layer, serio core, `SPIOCSTYPE` ioctl ABI, compat ioctl translation, TTY write wakeups, and serial input protocol drivers. It depends on userspace selecting the line discipline and setting the protocol expected by the target serio driver.

## Risks
`serport_ldisc_read()` sets `SERPORT_BUSY` before allocating the serio object and returns `-ENOMEM` without clearing it if allocation fails, leaving the ldisc instance busy until close. Protocol must be set before the read-side registration; changing it later does not affect an already registered port. Lifetime correctness depends on hangup/read/close ordering and on the TTY layer not freeing `disc_data` while read is sleeping.

## Test signals
Test privileged and unprivileged ldisc open, `SPIOCSTYPE` and compat ioctl packing, one-reader-only behavior, byte and flag forwarding, write wakeups to `serio_drv_write_wakeup()`, hangup unblocking read and unregistering serio, and serial protocol driver binding through `inputattach`.
