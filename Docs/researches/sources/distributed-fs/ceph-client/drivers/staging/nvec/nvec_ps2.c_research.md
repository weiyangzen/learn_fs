# sources/distributed-fs/ceph-client/drivers/staging/nvec/nvec_ps2.c

## Purpose
Serio PS/2 mouse/touchpad bridge for pointer data and commands transported by NVEC.

## Important APIs, Types, And Functions
`struct nvec_ps2` stores a serio port, notifier, and NVEC pointer. Key functions are `nvec_mouse_probe()`, `nvec_mouse_remove()`, `ps2_sendcommand()`, `ps2_startstreaming()`, `ps2_stopstreaming()`, `nvec_ps2_notifier()`, and PM suspend/resume callbacks.

## Control Flow
Probe allocates a `SERIO_8042` port named `nvec mouse`, fills write/start/stop callbacks, registers an NVEC notifier, and registers the serio port. Starting streaming sends `AUTO_RECEIVE_N` for six-byte packets; stopping sends cancel autoreceive. Serio writes send a synchronous NVEC PS/2 command and feed the response bytes back through `serio_interrupt()`. Asynchronous `NVEC_PS2_EVT` events and command responses are translated to serio interrupts.

## State And Persistence
Uses a static global `ps2_dev`, so only one controller/port is supported. Streaming state is held by EC commands and serio callbacks. No persistent storage exists.

## Dependencies And Integration Points
Depends on NVEC sync/async write APIs, NVEC notifiers, Linux serio/psmouse stack, platform MFD children, and PM sleep.

## Risks
Global singleton blocks multiple instances. Probe uses plain `kzalloc_obj()` for the serio port and relies on `serio_unregister_port()` for cleanup. Command response parsing assumes `msg[2] == 1` and length fields are sane. Remove/suspend send commands that can fail but ignore return values.

## Test Signals
Serio port registration, psmouse probe command exchange, streaming packet delivery, stop/cancel autoreceive, suspend disables and resume re-enables mouse, EC command timeout handling, and notifier unregister on removal.
