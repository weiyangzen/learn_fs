# sources/distributed-fs/ceph-client/include/uapi/linux/tty.h

Purpose: Defines public TTY line discipline numbers and the total line-discipline count.

Important APIs/types/functions: Constants map discipline IDs such as `N_TTY`, SLIP, PPP, AX.25, X.25, HDLC, Bluetooth HCI UART, SLCAN, PPS, GSM0710, NFC NCI, Speakup, MCTP, development/testing, and CAN327. `NR_LDISCS` is 31.

Control flow: Userspace passes these IDs to TTY ioctls such as `TIOCSETD`/`TIOCGETD`; the kernel switches or reports the line discipline for the TTY.

State and persistence behavior: Line discipline selection is per-TTY runtime state. It disappears when the TTY closes or is reset.

Dependencies and integration points: Integrates with TTY core, protocol line disciplines, serial drivers, and userspace tools configuring serial protocol stacks.

Risks: Numeric IDs are ABI. Removing or reusing values breaks userspace. Some disciplines are protocol parsers exposed to untrusted serial data, so selecting them has security and stability implications.

Test signals: Compile UAPI users, set/get representative disciplines on pseudo-terminals or serial test devices, and verify out-of-range IDs fail cleanly.
