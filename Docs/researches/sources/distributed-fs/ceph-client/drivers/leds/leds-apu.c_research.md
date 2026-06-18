# sources/distributed-fs/ceph-client/drivers/leds/leds-apu.c

## Purpose
Implements front-panel LEDs for PC Engines APU1 boards by directly writing AMD FCH GPIO MMIO bytes discovered by fixed addresses after DMI matching.

## Important APIs, Types, And Functions
`struct apu_led_profile` defines LED name, initial brightness, and MMIO offset. `struct apu_led_priv` embeds a classdev and mapped address. Global `apu_led` stores the platform device, LED array, and spinlock. Main functions are `apu1_led_brightness_set`, `apu_led_config`, `apu_led_probe`, `apu_led_init`, and `apu_led_exit`.

## Control Flow
Module init first checks strict DMI matches for PC Engines APU/APU1. If matched, it registers a simple platform device and probes the driver. Probe allocates global state, initializes the spinlock, maps three one-byte GPIO addresses, registers LED classdevs named `apu:green:1..3`, and writes initial brightness. Exit unregisters all LED classdevs and platform objects.

Brightness writes `APU1_LEDON` or `APU1_LEDOFF` to the mapped GPIO byte under a spinlock.

## State And Persistence
Global `apu_led` persists for module lifetime. Hardware state is direct MMIO GPIO output. LED brightness is restored by `LED_CORE_SUSPENDRESUME` via classdev flags and by initial writes at probe.

## Dependencies And Integration Points
Depends on DMI, platform devices, MMIO mapping, spinlocks, and LED class. It integrates only with APU1 boards; the code explicitly points APU2/3 users to another configuration.

## Risks
Fixed physical MMIO offsets are board-specific and would be unsafe without DMI gating. Global state makes the driver single-instance. Direct MMIO writes assume byte access semantics and no competing GPIO driver. Exit assumes probe completed enough to populate the LED array.

## Test Signals
On matching APU1 hardware, verify three LEDs register with expected initial states and write the correct GPIO values. On nonmatching systems, init should return `-ENODEV`. Suspend/resume should preserve class behavior through LED core support.
