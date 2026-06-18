# sources/distributed-fs/ceph-client/drivers/leds/leds-tca6507.c

Purpose: I2C driver for TI TCA6507, a 7-output LED/GPO controller with limited hardware brightness banks and two blink engines. It exposes selected outputs as LED class devices and optionally as output-only GPIOs.

Important APIs, types, and functions: `struct tca6507_chip` contains the shadow register file, pending register bitmask, bank allocation state, I2C client, work item, spinlock, LED array, and optional GPIO chip. `choose_times()` maps requested millisecond delays to hardware time-code pairs. `led_prepare()`, `led_release()`, and `led_assign()` allocate brightness/blink banks. `tca6507_work()` writes dirty registers asynchronously. `tca6507_led_dt_init()` builds platform-data-like LED info from child nodes.

Control flow: probe validates I2C support and DT children, allocates chip state, registers LED devices for non-GPIO child entries, registers GPIOs for child entries compatible with `gpio`, initializes all registers to zero through scheduled work, and returns. Brightness and blink callbacks update per-LED desired state, re-run bank allocation under spinlock, and schedule I2C work if any shadow register changed.

State and persistence: the shadow `reg_file` is the driver's source of desired hardware state. Bank use counters track shared hardware brightness/timing resources and are recalculated when LEDs change. Hardware writes are asynchronous, so remove cancels work to flush/stop pending I2C operations.

Dependencies and integration points: I2C, LED class, optional gpiolib, firmware property parsing, workqueues, and compatible `ti,tca6507`.

Risks and test signals: the allocator is the main risk: test bank sharing, default vs explicit blink delays, fallback to software blink on unsupported times, brightness approximation, GPIO inverse semantics, work cancellation on remove, and concurrent LED/GPIO operations.
