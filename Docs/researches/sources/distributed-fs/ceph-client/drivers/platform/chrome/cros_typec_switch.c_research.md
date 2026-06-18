<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_switch.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_switch.c

## Purpose

This platform driver registers Type-C mode-switch and retimer devices whose actual hardware is controlled by the Chrome EC. It translates Type-C mux/retimer set requests into `EC_CMD_TYPEC_CONTROL` mux commands and waits for EC completion events.

## Important APIs, Types, And Functions

`struct cros_typec_port` stores a port number plus registered `typec_mux_dev` and `typec_retimer`. `struct cros_typec_switch_data` stores the parent EC and per-port table. `cros_typec_get_mux_state()` maps Type-C core modes and DP pin assignments to EC USB PD mux flags. `cros_typec_configure_mux()` clears the relevant event, sends `TYPEC_CONTROL_COMMAND_USB_MUX_SET`, and polls `EC_CMD_TYPEC_STATUS` for `PD_STATUS_EVENT_MUX_*_SET_DONE`. Probe walks firmware child nodes and registers mode-switch and/or retimer objects.

## Control Flow

Probe gets the Chrome EC pointer from the parent device and enumerates child fwnodes. Each child `_ADR` selects the EC Type-C port index. Presence of `retimer-switch` registers a retimer with mux index 1; presence of `mode-switch` registers a mode switch with mux index 0. Runtime `set` callbacks call the shared configure helper, which clears stale completion events, sends a new state to the EC, and polls for up to one second.

## State And Persistence

State is per platform device and tracks registered switch objects by EC port number. The mux state itself persists in EC-controlled hardware until changed, disconnect, reset, or power transition. No state is cached after each command completes.

## Dependencies And Integration Points

It depends on ACPI child fwnodes, local address `_ADR`, Chrome EC Type-C host commands, USB Type-C mux and retimer frameworks, and DisplayPort altmode constants. ACPI ID is `GOOG001A`.

## Risks

Polling with sleeps can delay mux operations up to one second. If EC event clearing or status reporting is racy, the driver can time out after a successful physical switch. Only DP altmodes are recognized for modal state mapping; unsupported modes return `-EOPNOTSUPP`. Firmware child-node properties must match Type-C connector graph expectations.

## Test Signals

Exercise child-node discovery, invalid `_ADR`, mode-switch and retimer registration, USB safe/USB/DP pin assignment state mapping, EC mux command failure, event timeout, unplug/replug sequences, and concurrent set callbacks for different ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_typec_switch.c -->
