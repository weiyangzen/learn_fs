<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cyberjack.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/cyberjack.c

Purpose: REINER SCT cyberJack pinpad/e-com chipcard reader USB serial driver with interrupt announcements and framed bulk transfers. The complete 422-line source was read.

Important APIs/types/functions: `struct cyberjack_private`, `cyberjack_port_probe()`, `cyberjack_open()`, `cyberjack_close()`, `cyberjack_write()`, `cyberjack_write_room()`, `cyberjack_read_int_callback()`, `cyberjack_read_bulk_callback()`, and `cyberjack_write_bulk_callback()`.

Control flow and state: probe allocates state and submits interrupt-in URB. Open clears bulk-out halt and resets counters. Writes accumulate protocol frames in a 320-byte buffer until the length from bytes 1-2 plus header is available, then submit bulk chunks; write completion sends remaining chunks. Interrupts announce pending bulk-in bytes in `rdtodo`; bulk reads push data to tty and resubmit until `rdtodo` is drained. State is spinlock-protected `rdtodo`, `wrbuf`, `wrfilled`, and `wrsent`.

Dependencies and integration points: USB serial URBs, tty flip buffering, write-URB free bit, and softint notification. No termios or modem-control support is implemented.

Risks and test signals: risks include fixed write buffer, dropped data on overflow/submit failure, constant `write_room()`, interrupt URB active before open, length validation gaps, and callback races on close. Test partial/full/oversized writes, multi-URB writes, interrupt announcements, rdtodo overflow handling, close/remove with active URBs, and real reader transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/cyberjack.c -->
