# sources/distributed-fs/ceph-client/drivers/mfd/ipaq-micro.c

Purpose: MFD driver for the Compaq iPAQ h3xxx Atmel microcontroller companion. It implements the custom serial protocol, queues synchronous messages, dispatches asynchronous keyboard/touchscreen events, and registers backlight, battery, key, touchscreen, and LED children.

Important APIs/types/functions: exported `ipaq_micro_tx_msg()`, `ipaq_micro_trigger_tx()`, `micro_process_char()`, `micro_rx_msg()`, `micro_serial_isr()`, `micro_reset_comm()`, and `micro_probe()`.

Control flow: probe maps UART and SDLC resources, resets serial communication, requests the shared IRQ, initializes queue/lock state, registers MFD cells, queries version, and dumps EEPROM data. TX messages are framed with SOF, id/length, payload, and checksum; RX is parsed by a small state machine and matched to pending synchronous messages or callbacks.

State and persistence: driver state includes current message, queued messages, RX/TX protocol state, callback hooks, and firmware version. EEPROM data is read for reporting and serial-number entropy but not written here.

Dependencies and integration: depends on SA1100-style UART registers, platform resources, `linux/mfd/ipaq-micro.h`, MFD child drivers, completions in message objects, and callbacks registered by input children.

Risks: locking spans callback dispatch and message completion; malformed checksum silently drops frames. `micro_tx_chars()` disables TX interrupts after each FIFO drain, so progress depends on the ISR/trigger model. EEPROM string conversion is simplistic.

Test signals: version request completion, queued synchronous message ordering, keyboard/touchscreen callback delivery, UART error logging, suspend/resume reinitialization, EEPROM dump, and child driver interactions.
