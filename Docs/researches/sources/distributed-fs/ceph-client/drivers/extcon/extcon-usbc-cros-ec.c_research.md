# sources/distributed-fs/ceph-client/drivers/extcon/extcon-usbc-cros-ec.c

## Purpose
ChromeOS Embedded Controller USB-C extcon provider. It queries EC USB PD commands for a selected port and reports USB device, USB host, and DisplayPort extcon states with VBUS, polarity, SuperSpeed, and HPD properties.

## Important APIs, Types, and Functions
`struct cros_ec_extcon_info` stores device, extcon, port ID, EC device, notifier block, cached data role, power role, DP state, USB mux state, and power type. `cros_ec_pd_command()` allocates and transfers EC command buffers. Helper queries fetch power type, PD mux flags, current PD role/polarity, and number of ports. `extcon_cros_ec_detect_cable()` is the main state reconciliation function, mapping EC role/mux/power responses to extcon states and properties. `extcon_cros_ec_event()` handles EC host events. Probe validates port ID, registers extcon properties, registers the EC notifier, and performs initial detection.

## Control Flow
Probe reads `google,usb-port-id` or uses platform ID, queries EC port count, registers extcon, sets property capabilities, initializes cached state, registers a blocking notifier on `ec->event_notifier`, and forces initial detection. Runtime updates are notifier-driven: PD MCU or USB mux host events call detection. Detection first gets power type, then role/polarity; disconnected role returns `-ENOTCONN` and leaves data role none. If connected, it gets mux flags and derives DisplayPort, USB mux, and HPD. It suppresses UFP reporting for charger-only wall-wart types. If cached state changed or force is true, it updates all extcon states/properties and syncs USB, USB_HOST, and DP; HPD-only events can sync DP without role changes.

## State and Persistence
Cached fields in `cros_ec_extcon_info` prevent redundant extcon updates and allow HPD-only handling. All durable connection truth comes from EC command responses. No hardware registers are directly programmed by this driver.

## Dependencies and Integration Points
Uses ChromeOS EC protocol commands (`EC_CMD_USB_PD_*`), EC event notifier, extcon provider, OF, platform device core, and USB PD command structures. It integrates with consumers through extcon and with EC transport through `cros_ec_cmd_xfer_status()`.

## Risks
The wall-wart classifier has a FIXME noting some USB-C chargers are intentionally miscategorized to avoid breaking cables/peripherals. PD mux query failure falls back to USB enabled, which may over-report SuperSpeed. EC command allocation occurs on each detection. If initial detection fails after notifier registration, probe unregisters correctly; runtime detection errors just log and keep previous extcon state. Polarity properties are updated even for DP and both USB roles during state changes.

## Test Signals
Test disconnected, DFP, UFP, charger-only, DP alt mode, USB mux on/off, HPD IRQ-only, EC command failures, invalid port IDs, notifier unregister on remove, and resume forced detection. Extcon property checks should include VBUS, Type-C polarity, USB_SS, and DP HPD.
