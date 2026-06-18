# sources/distributed-fs/ceph-client/drivers/input/joystick/turbografx.c

Purpose: supports TurboGraFX parallel-port joystick adapters, allowing up to seven configured gamepads per parport with 1-5 buttons.

Important APIs/types/functions: `struct tgfx_config` holds module parameter maps. `struct tgfx` stores the parport device, polling timer, input devices, names, phys paths, stick mask, usage count, parport number, and mutex. Key functions are `tgfx_timer`, `tgfx_open`, `tgfx_close`, `tgfx_attach`, `tgfx_detach`, `tgfx_init`, and `tgfx_exit`.

Control flow: module parameters `map`, `map2`, and `map3` select parport numbers and per-port button counts. Init refuses to load without configured devices and registers a parport driver. Attach claims only configured ports, registers an exclusive parport device, allocates state, creates input devices for valid joystick slots, and stores the instance globally. Opening the first input claims the parport, sets control lines, and starts a 10 ms timer. The timer selects each stick by writing data, reads status/control bits, reports two digital axes and up to five buttons, syncs, and reschedules itself. Closing the last user stops the timer and releases the port.

State and persistence: configuration comes from module parameters. Runtime state tracks active users and devices in memory only. No persistent hardware state remains after close except the port control value reset to zero.

Dependencies and integration: uses parport, timer_list, jiffies, mutex helpers, and Linux input. Devices are reported as `BUS_PARPORT`.

Risks: polling is timer based and assumes exclusive parport access. Invalid module maps prevent devices from appearing. Attach error unwinding must unregister already registered input devices. Electrical and CAVEAT parport control-bit behavior is adapter-specific.

Test signals: load with valid/invalid maps, verify each configured slot appears, check timer starts only on first open and stops on last close, confirm parport claim/release, and validate direction/button bit mapping with `evtest`.
