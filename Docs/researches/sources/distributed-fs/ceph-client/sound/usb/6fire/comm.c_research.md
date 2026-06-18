# sources/distributed-fs/ceph-client/sound/usb/6fire/comm.c

## Purpose
Implements 6Fire device command transport and inbound interrupt receiver on endpoint 1. It also dispatches inbound MIDI packets to the MIDI runtime.

## Important APIs, Types, and Functions
Public functions are `usb6fire_comm_init()`, `usb6fire_comm_abort()`, and `usb6fire_comm_destroy()`. Runtime callbacks assigned into `struct comm_runtime` are `init_urb`, `write8`, and `write16`. Internal helpers include `usb6fire_comm_receiver_handler()`, `usb6fire_comm_init_buffer()`, and `usb6fire_comm_send_buffer()`.

## Control Flow
Initialization allocates `comm_runtime`, a 64-byte receiver buffer, configures a receive interrupt URB on endpoint 1, submits it, and stores function pointers for other submodules. The receive completion checks packet id `0x10` for MIDI input and calls `midi_rt->in_received()` with payload bytes. Unless `chip->shutdown` is set, the handler resubmits the receiver URB. Writes allocate a 13-byte temporary buffer, encode request-specific packet layouts, synchronously send with `usb_interrupt_msg()`, validate transferred length, then free the buffer.

## State and Persistence
State includes the receiver URB, receiver buffer, chip pointer, serial field, and function pointers. The receiver URB persists from init until abort/destroy. No device settings are cached here beyond transient command buffers.

## Dependencies and Integration Points
Used by `control.c` to write mixer/rate/channel registers, by `midi.c` to initialize its output URB through `init_urb`, and by `chip.c` for lifecycle. Depends on USB interrupt pipes and 6Fire endpoint protocol.

## Risks
`write16` declaration in `comm.h` names `vh, vl` while implementation expects `vl, vh`; callers in this tree pass low then high and the function pointer type is positional, but naming can mislead future edits. Receive handler resubmission failures only warn. Temporary command allocation on every mixer write can fail under memory pressure. Destroy assumes abort already stopped the URB.

## Test Signals
Exercise all request types (`0x02`, `0x12`, `0x20`-`0x22`), short transfer error handling, inbound MIDI dispatch, receiver resubmit on normal completions, and no resubmit after shutdown/poison.
