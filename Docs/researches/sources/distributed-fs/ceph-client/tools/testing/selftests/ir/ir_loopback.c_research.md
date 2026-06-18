# sources/distributed-fs/ceph-client/tools/testing/selftests/ir/ir_loopback.c

`ir_loopback.c` validates IR protocol encode/decode through the `rc-loopback` driver. It sends random LIRC scancodes for many protocols and expects the loopback receiver to decode the same protocol and scancode.

Important interfaces are `linux/lirc.h`, `LIRC_SET_REC_MODE`, `LIRC_SET_SEND_MODE`, `LIRC_MODE_SCANCODE`, `struct lirc_scancode`, `/sys/class/rc/<rcN>/protocols`, `/dev/lirc*`, `poll()`, `read()`, and `write()`. The `protocols[]` table maps `enum rc_proto` values to names, masks, and decoder names. `lirc_open()` discovers a lirc character device under a sysfs rc device.

`main()` opens the receiver and sender rc devices supplied on the command line, sets scancode receive/send mode, opens the receiver protocol sysfs file, loops over all protocol table entries, enables the required decoder, generates ten valid random scancodes per protocol, writes each scancode to the sender, polls the receiver, reads the decoded scancode, and records pass or error.

Kernel state includes selected decoders, lirc device queues, and rc-loopback transmit/receive state. Dependencies are root access, `rc-loopback`, LIRC UAPI, sysfs protocol controls, and kselftest reporting. Risks are decode scheduling latency, random invalid-code filtering, and multiple protocol variants sharing decoders. Pass signals are matching protocol/scancode pairs and zero fail/error count.
