# sources/distributed-fs/ceph-client/drivers/misc/ibmasm/remote.c

## Purpose
`remote.c` converts remote mouse and keyboard events from IBM ASM service-processor MMIO queues into Linux input events.

## Important APIs, Types, and Functions
Public functions are `ibmasm_handle_mouse_interrupt()`, `ibmasm_init_remote_input_dev()`, and `ibmasm_free_remote_input_dev()`. Internal helpers include key translation tables `xlate_high` and `xlate`, `print_input()`, `send_mouse_event()`, and `send_keyboard_event()`.

## Control Flow
Initialization allocates mouse and keyboard input devices, fills PCI IDs and capability bits, registers them, and enables mouse interrupts. The low-level interrupt handler calls `ibmasm_handle_mouse_interrupt()` when the remote queue has an interrupt. That function reads queue reader/writer indices, copies each remote input entry from MMIO, emits absolute mouse/button events or translated key events, advances the queue reader, and stops on invalid queue indices or unknown input type. Cleanup disables mouse interrupts and unregisters devices.

## State and Persistence
State is in `sp->remote.mouse_dev` and `sp->remote.keybd_dev`; queue reader/writer and display settings live in service-processor MMIO. Input state is reported to the kernel input subsystem and not stored by this file beyond registered devices.

## Dependencies and Integration Points
It depends on PCI device metadata, Linux input core, remote register macros from `remote.h`, and low-level interrupt dispatch. `ibmasmfs` separately exposes remote video settings.

## Risks and Edge Cases
Key translation indexes use 8-bit tables; unmapped keysyms report key code 0/`KEY_RESERVED`. Invalid reader/writer indices reset the reader to zero. Cleanup assumes input devices were registered. Mouse maximums are fixed constants rather than read from hardware.

## Test Signals
Feed MMIO queue entries for mouse buttons/movement, standard and high keysyms, unmapped keys, queue wrap, invalid indices, init failure at keyboard registration, and interrupt disable/unregister ordering.
