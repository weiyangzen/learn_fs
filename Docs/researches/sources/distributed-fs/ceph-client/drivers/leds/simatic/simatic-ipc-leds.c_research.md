<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c -->
# sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c

Purpose: This is the legacy direct-I/O SIMATIC IPC LED class driver for platforms whose LEDs are controlled through a two-byte I/O port at `0x404E`.

Important APIs, types, and functions: `struct simatic_ipc_led` binds an active-low bit mask, LED name, and `led_classdev`. `simatic_ipc_led_set_io()` reads the port, sets or clears the LED bit, and writes it back under a spinlock. `simatic_ipc_led_get_io()` reads the active-low bit. `simatic_ipc_leds_probe()` validates the SIMATIC device mode, requests the I/O region, handles byte-swapping for `SIMATIC_IPC_DEVICE_227D`, and registers all LED class devices.

Control flow: Probe accepts `SIMATIC_IPC_DEVICE_227D` and `SIMATIC_IPC_DEVICE_427E`. For 227D, the bit values in the static LED table are byte-swapped once because the two I/O bytes are wired in the opposite order. Each table entry gets brightness set/get callbacks, max brightness `LED_ON`, and a fixed color/function name.

State and persistence: LED state persists only in the hardware I/O port. A global spinlock serializes read-modify-write access to the shared register. The static LED table is mutated for 227D byte swapping, so this driver assumes a single platform instance and a stable `devmode`.

Dependencies and integration: It integrates with `LEDS_CLASS`, `SIEMENS_SIMATIC_IPC` platform data, x86 I/O port accessors, and platform-device probing through module alias `platform:KBUILD_MODNAME`.

Risks and test signals: Static table mutation for 227D can be wrong if multiple different SIMATIC devices were ever probed in one kernel. Active-low semantics are easy to invert. Test I/O resource contention, 227D and 427E bit mappings, LED get after set, and failure when unsupported `devmode` is provided.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/simatic/simatic-ipc-leds.c -->
