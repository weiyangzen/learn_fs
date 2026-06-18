# sources/distributed-fs/ceph-client/drivers/input/mouse/rpcmouse.c

`rpcmouse.c` is the Acorn RiscPC host mouse driver. It reads IOMD mouse X/Y counters and button state on every VSYNC interrupt, computes deltas, and reports a relative input device.

`rpcmouse_init()` allocates the single input device, fills identity/capabilities, captures initial counter values, requests shared `IRQ_VSYNCPULSE`, and registers input. `rpcmouse_irq()` reads `IOMD_MOUSEX`, `IOMD_MOUSEY`, and button MMIO, updates last counters, reports `REL_X`, inverted `REL_Y`, and three buttons. Exit frees the IRQ and unregisters input.

State is only previous X/Y counters and the input pointer. Dependencies are ARM RiscPC/IOMD headers, raw MMIO, IRQ infrastructure, and input. Risks are counter wraparound, fixed hardware addresses, button polarity assumptions, and IRQ allocation failure. Test signals are IRQ registration, movement deltas, Y direction, button mapping, and clean init/exit error paths on supported hardware.
