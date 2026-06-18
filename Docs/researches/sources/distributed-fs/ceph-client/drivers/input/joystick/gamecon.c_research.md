# sources/distributed-fs/ceph-client/drivers/input/joystick/gamecon.c

Purpose: Parallel-port adapter driver for several console controllers: NES, SNES, SNES mouse, N64, multisystem joysticks, PSX pads, and PSX DDR mats. It is entirely module-parameter configured and multiplexes up to five devices per parport.

Important APIs/types/functions: `struct gc_config` stores parport/pad-type parameter lists. `enum gc_type` identifies pad protocols. `struct gc` owns pardevice, pad array, timer, pad type counts, open count, parport number, and mutex. `gc_setup_pad()` allocates and configures each input device. Protocol paths include `gc_n64_read_packet()`/`gc_n64_process_packet()`/`gc_n64_play_effect()`, `gc_nes_read_packet()`/`gc_nes_process_packet()`, `gc_multi_process_packet()`, and `gc_psx_read_packet()`/`gc_psx_report_one()`.

Control flow: Init validates `map`, `map2`, or `map3`, then registers a parport driver. Attach matches configured parport, registers an exclusive pardevice, allocates the `struct gc`, and creates each requested pad. Open claims the parport and starts a 100 Hz timer. The timer runs protocol processors in a fixed order: N64 first, NES/SNES/SNES mouse, multisystem, then PSX. Close stops the timer and releases the parport.

State and persistence: Per-parport state lives in `gc_base[]`; per-pad state includes type, input device, and phys path. N64 force-feedback subdevice context stores pad index for rumble. No persistent storage exists.

Dependencies and integration points: Uses parport control/data/status lines, input core, input FF memless for N64 rumble, timers, and module parameters. `psx_delay` tunes PSX bit timing.

Risks: All protocols are timing-sensitive and share one polling timer, with comments noting N64 controllers are confused by reads for about 200 us. Misconfigured pad types can drive the wrong lines. N64 rumble sends long command sequences with interrupts disabled. PSX reads use the longest detected packet length across all pads and can be affected by weak responses.

Test signals: Module parameter validation and multiple parport instances; NES/SNES button maps; SNES mouse ID filtering and relative axes; N64 axes/buttons/rumble; PSX digital, analog, rumble, DDR reports; open/close parport claim behavior and timer rescheduling.
