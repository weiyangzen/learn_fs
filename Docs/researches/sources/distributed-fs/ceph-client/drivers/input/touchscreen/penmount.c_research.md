<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/penmount.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/penmount.c

Purpose: serio driver for PenMount RS-232 touchscreen protocols. It supports single-touch 9000/6000 packet formats and multitouch 3000/6250 formats, validates checksums where present, and reports input through absolute and multitouch events.

Important APIs/types/functions: `struct pm` stores input, serio, packet index/data, packet size, max contacts, slot cache, and parser function pointer. `struct mt_slot` stores per-contact x/y/active. Parser functions are `pm_parse_9000()`, `pm_parse_6000()`, `pm_parse_3000()`, and `pm_parse_6250()`. `pm_checkpacket()` validates six-byte checksum formats, `pm_mtevent()` emits MT slots plus pointer emulation, `pm_interrupt()` feeds bytes to the selected parser, and connect/disconnect manage serio and input lifetimes.

Control flow: connect chooses packet size, parser, product ID, coordinate max, and max contact count based on `serio->id.id`; initializes ABS axes and MT slots when needed; opens serio; and registers input. Each received byte is stored at the current index and passed to the parser. A parser verifies header bits and packet length, optionally validates checksum, decodes coordinates/touch/slot state, reports single-touch or updates a cached MT slot and emits all slots.

State and persistence: state is the packet buffer/index and cached multitouch slots. No controller configuration or persistent data is written.

Dependencies/integration: depends on serio `SERIO_PENMOUNT`, Linux input and MT core, and RS-232 packet formats for PenMount model families.

Risks and test signals: parser synchronization depends on header checks and does not scan for headers mid-packet. Test corrupted bytes, checksum failures, slot numbers for 3000/6250 staying below `maxcontacts`, disconnect during interrupt activity, MT pointer emulation, coordinate max by model, and packet size differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/penmount.c -->
