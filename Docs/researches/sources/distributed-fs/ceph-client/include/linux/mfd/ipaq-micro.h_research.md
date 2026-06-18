# sources/distributed-fs/ceph-client/include/linux/mfd/ipaq-micro.h

Purpose: This header defines the Compaq iPAQ microcontroller MFD protocol and parent state. It models the serial packet parser, transmit queue, message format, synchronous/asynchronous message helpers, and callbacks for keyboard and touchscreen events.

Important APIs, types, and functions: Message IDs cover version, keyboard, touchscreen, EEPROM, thermal sensor, LEDs, battery, SPI, backlight, codec, and display control. `enum rx_state` models SOF, ID, data, and checksum parser states. `struct ipaq_micro_txdev` and `struct ipaq_micro_rxdev` hold ISR transmit/receive parser state. `struct ipaq_micro_msg` stores command ID, TX/RX buffers, completion, and queue node. `struct ipaq_micro` stores MMIO bases, version, TX/RX state, spinlock, active message, queue, and async key/touch callbacks. `ipaq_micro_tx_msg` is exported; inline `ipaq_micro_tx_msg_sync` initializes completion, sends, and waits, while `ipaq_micro_tx_msg_async` sends without waiting.

Control flow, state, and persistence: TX messages are queued and emitted through interrupt-driven serial state; RX bytes advance the parser state machine and complete the matching message or dispatch async key/touch callbacks. Driver state is queue, current message, parser indices, checksum, and callbacks. Persistent device state includes microcontroller firmware behavior and EEPROM contents.

Dependencies and integration points: It depends on spinlocks, completions, and lists. It integrates with platform children for battery, LEDs/backlight, input keyboard/touchscreen, thermal, EEPROM, SPI, and legacy audio/display controls.

Risks and test signals: Risks include waiting forever in `ipaq_micro_tx_msg_sync` if no completion occurs, buffer length overruns, checksum/parser resync bugs, callback lifetime issues, and locking mistakes in ISR context. Test signals include malformed packet parser tests, TX queue ordering, timeout coverage in callers, async key/touch event delivery, EEPROM read/write, and suspend/resume serial recovery.
