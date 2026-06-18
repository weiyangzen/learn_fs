# sources/distributed-fs/ceph-client/drivers/media/pci/bt8xx/bttv-input.c

## Purpose
`bttv-input.c` implements infrared remote-control support for selected bttv boards. It handles GPIO-polled remotes, GPIO IRQ remotes, a legacy GPIO RC5 decoder for Nebula DigiTV, and I2C IR receiver instantiation for cards with external IR chips.

## Important APIs, Types, And Functions
Entry points called by the main driver are `init_bttv_i2c_ir()`, `bttv_input_init()`, `bttv_input_fini()`, and `bttv_input_irq()`. GPIO key paths are `ir_handle_key()` and `ir_enltv_handle_key()`. RC5 handling uses `bttv_rc5_irq()`, `bttv_rc5_timer_end()`, and `bttv_rc5_decode()`. I2C IR support includes `get_key_pv951()` and `i2c_new_scanned_device()` setup. Runtime state is `struct bttv_ir` from `bttvp.h` plus an `rc_dev`.

## Control Flow
During bttv probe, `init_bttv_i2c_ir()` may instantiate an `ir_video` I2C client, then `bttv_input_init()` selects masks, polling interval, keymap, or RC5 mode based on `btv->c.type`. It configures GPIO direction, allocates/registers an rc-core device, and starts polling or RC5 completion timers. Interrupts from the main bttv IRQ handler call `bttv_input_irq()`, which dispatches to RC5 or GPIO decoding. Polling timers periodically read GPIO, extract keycode bits, and emit `rc_keydown*()`/`rc_keyup()`.

## State And Persistence
Remote state includes key masks, last GPIO value, RC5 bit accumulation, base timestamp, active flag, timer, keymap name, and rc-core device. The state lasts for the PCI device lifetime and is freed by `bttv_input_fini()`. No persistent configuration is stored beyond module parameters `ir_debug` and `ir_rc5_remote_gap`.

## Dependencies And Integration Points
This file depends on `rc-core`, Linux input, I2C client creation, bttv GPIO helpers, bttv board IDs/keymaps, and the main IRQ path. It requests `ir-kbd-i2c` when built as a module. Remote capability is advertised by card tables via `has_remote`.

## Risks
The board switch hardcodes many GPIO masks and keymaps; wrong masks cause stuck keydown, missing keyup, or noisy input. RC5 decoding is deliberately legacy and timing-sensitive, using GPIO edge timing and a timer endpoint. `bttv_input_fini()` unregisters and then frees the rc device pointer, so lifecycle changes must respect rc-core ownership. Poll intervals as low as 1 ms can increase CPU wakeups on affected hardware.

## Test Signals
Expected signals are registered rc-core devices with correct keymaps, `ir-keytable` visibility, key events from GPIO and I2C remotes, no repeated stuck keys, correct RC5 toggle handling on Nebula DigiTV, and clean teardown without timer warnings.
