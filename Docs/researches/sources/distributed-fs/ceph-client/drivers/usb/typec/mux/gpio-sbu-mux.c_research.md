<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/gpio-sbu-mux.c -->
# sources/distributed-fs/ceph-client/drivers/usb/typec/mux/gpio-sbu-mux.c

## Purpose

`gpio-sbu-mux.c` implements a simple platform Type-C SBU mux using GPIOs for enable and lane select.

## Important APIs, Types, and Functions

`struct gpio_sbu_mux` stores optional enable GPIO, required select GPIO, switch/mux devices, mutex, and cached enabled/swapped booleans. Key functions are `gpio_sbu_switch_set()`, `gpio_sbu_mux_set()`, `gpio_sbu_mux_probe()`, and `gpio_sbu_mux_remove()`.

## Control Flow

Probe obtains GPIOs, registers a Type-C orientation switch and mode mux on the platform device fwnode, and stores drvdata. Orientation NONE disables, NORMAL clears swap, and REVERSE sets swap. Mux state enables SBU only for DP C/D/E and disables for safe/USB. Remove forces enable low and unregisters mux/switch devices.

## State and Persistence Behavior

Cached `enabled` and `swapped` mirror GPIO outputs and are protected by a mutex. Hardware state is the GPIO output levels; no persistent storage exists.

## Dependencies and Integration Points

The driver depends on platform devices, GPIO descriptors, Type-C mux/switch core, and DP state constants. It is useful for boards where SBU routing is implemented by discrete GPIO-controlled analog switches.

## Risks and Test Signals

Risks include returning `-EOPNOTSUPP` from mux set when no enable GPIO exists even though switch routing can still work, no validation that selected modes are DP altmodes by SVID, and ordering between orientation and mux calls affecting when enable/select outputs change. Test signals include probe with and without optional enable GPIO, normal/reverse orientation toggling select, safe/USB disabling, DP C/D/E enabling, removal disabling output, and concurrent orientation/mode updates under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/typec/mux/gpio-sbu-mux.c -->
