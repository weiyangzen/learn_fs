## sources/distributed-fs/ceph-client/drivers/input/keyboard/ipaq-micro-keys.c

Purpose: iPAQ h3600 Atmel micro companion key subdevice. It exposes nine fixed PDA button/navigation keycodes from messages delivered by the parent `ipaq_micro` MFD.

Important APIs/types/functions: `struct ipaq_micro_keys` contains the parent micro device, input device, and mutable keycode copy. `micro_key_receive()` decodes a one-byte message with bit 7 as down state and low 7 bits as key index. `micro_key_start()` and `micro_key_stop()` install/remove the parent callback under `micro->lock`.

Control flow: probe allocates input, copies the fixed `micro_keycodes`, sets `EV_KEY` capabilities, and registers open/close callbacks. Opening the input device hooks the parent callback; closing unhooks it. Suspend unconditionally stops receiving, and resume reattaches only if the input device is enabled.

State/dependencies/integration: state is the parent callback pointer and keycode array. It depends on `linux/mfd/ipaq-micro.h`, parent driver locking, platform-device binding, input core, and PM callbacks.

Risks and test signals: message length is not validated before reading `msg[0]`, so parent callback contract must guarantee at least one byte. Index 0 is accepted but the table comment starts at 1; tests should confirm parent numbering. Validate open/close races, suspend/resume while open, and unknown key index suppression.
