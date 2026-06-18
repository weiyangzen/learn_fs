# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43/leds.h

This header declares b43 LED structures, behavior constants, and lifecycle APIs, with no-op stubs when `CONFIG_B43_LEDS` is disabled. Enabled builds define `struct b43_led`, `struct b43_leds`, `B43_MAX_NR_LEDS`, `B43_LED_BEHAVIOUR`, `B43_LED_ACTIVELOW`, and `enum b43_led_behaviour`.

The state model stores four logical LEDs (TX, RX, radio, assoc), a stop flag, and a work item. Each LED tracks the owning `b43_wl`, LED class device, GPIO index, active-low wiring, name, requested brightness, and hardware state. Disabled builds keep `struct b43_leds` empty and compile lifecycle calls away.

Integration points are Linux LED class, workqueues, mac80211 LED triggers via `leds.c`, and SPROM GPIO behavior values. Risks are API drift between enabled and disabled builds, the FIXME `B43_LED_WEIRD` behavior, and fixed LED name length. Test signals are builds with/without LED support and runtime LED class device creation only when enabled.
