<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-netdev.c -->
# sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-netdev.c

Purpose: The netdev trigger drives LEDs from a named network interface's link, speed, duplex, RX/TX, and error activity. It can either use software polling/blinking or offload supported modes to LED hardware control.

Important APIs and state: `struct led_netdev_data` stores a mutex, delayed work, netdevice notifier, LED pointer, held `net_device`, selected device name, blink interval, last activity counter, mode bitset, cached link speed/duplex/supported modes, carrier state, and hardware-control flag. Sysfs attributes include `device_name`, link and speed bits, half/full duplex, rx/tx/error bits, `interval`, and readonly `offloaded`.

Control flow: Activation allocates state, initializes interval, detects existing hardware-control default, sets trigger data, and registers a netdevice notifier. `device_name_store()` cancels work, takes RTNL then the trigger mutex, swaps the held netdevice reference, refreshes link state, and updates baseline LED state. Mode stores validate mutually exclusive generic link vs speed-specific modes, recompute hardware-control suitability, and set a baseline. Netdevice notifier responds to up/down/change/register/unregister/rename events for the tracked device, updates cached state, refreshes link-speed sysfs visibility, and resets baseline. Delayed work samples stats, detects selected activity counter changes, and blinks oneshot with inversion if link baseline is on.

State and persistence: Per-LED trigger state owns a netdevice reference when configured and persists until deactivation. Hardware offload state is delegated through LED class `hw_control_*` callbacks when available and valid. Software state uses delayed work and cached last activity.

Dependencies and integration: It depends on NET, ethtool link settings, RTNL locking, netdevice notifier chain, LED trigger core, optional LED hardware-control callbacks, and sysfs attribute groups with dynamic visibility for supported link speeds.

Risks and test signals: Lock ordering is explicit: RTNL before trigger mutex in device-name changes. `dev_put(trigger_data->net_dev)` is called in several paths and must handle NULL safely. Hardware-control mode rejects non-default intervals and mismatched associated netdevs. Test rename/register/unregister, interface removal while work is queued, speed attribute visibility, unsupported offload fallback, LEDs without software brightness callbacks, all mode-bit combinations, and RX/TX/error polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/leds/trigger/ledtrig-netdev.c -->
