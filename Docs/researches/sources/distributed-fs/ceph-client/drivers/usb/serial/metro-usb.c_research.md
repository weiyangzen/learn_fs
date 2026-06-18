# sources/distributed-fs/ceph-client/drivers/usb/serial/metro-usb.c

## Purpose
This driver supports Metrologic/Honeywell USB POS/scanner devices in bidirectional and unidirectional modes. It exposes a one-port USB serial interface using interrupt-in reads, optional interrupt-out mode commands for unidirectional devices, and simple modem-control state for RTS/DTR.

## Important APIs, Types, and Functions
`struct metrousb_private` stores a spinlock, throttle flag, and cached modem control state. Important functions include `metrousb_is_unidirectional_mode`, `metrousb_calc_num_ports`, `metrousb_send_unidirectional_cmd`, `metrousb_read_int_callback`, `metrousb_open`, `metrousb_cleanup`, `metrousb_set_modem_ctrl`, `metrousb_port_probe`, `metrousb_port_remove`, `metrousb_throttle`, `metrousb_unthrottle`, `metrousb_tiocmget`, and `metrousb_tiocmset`.

## Control Flow
Probe allocates private state. `calc_num_ports` enforces that unidirectional devices expose an interrupt-out endpoint because open/close commands are sent there. Open clears private state, clears halt on the interrupt-in pipe, fills the interrupt-in URB with the driver callback and interval 1, submits it, then sends `UNI_CMD_OPEN` if the product is unidirectional. Close kills the interrupt-in URB and sends `UNI_CMD_CLOSE`.

Read callbacks push any received interrupt payload to the TTY flip buffer, check whether the port has been throttled, and resubmit the interrupt URB only when not throttled. Throttle sets the flag and lets the current callback stop resubmission; unthrottle clears the flag and submits the URB again. `TIOCMSET` updates cached RTS/DTR state under the spinlock and sends a vendor control request intended to set modem control.

## State and Persistence
State is entirely per-port and volatile: current throttle flag and cached `TIOCM_*` control state. Device mode is derived from product ID each time. Unidirectional open/close state is maintained in device firmware after interrupt-out commands.

## Dependencies and Integration Points
The file depends on USB serial interrupt endpoint handling, TTY flip buffers, spinlocks, and vendor control/interrupt messages. It registers device IDs for `0x0c2e:0x0720`, `0x0c2e:0x0700`, and an MS7820 interface-class match. User-space integration is conventional serial reads plus modem-control ioctls.

## Risks
`metrousb_set_modem_ctrl` computes an `mcr` value but passes `control_state` as the USB request value rather than `mcr`; this may be intentional for firmware or a bug worth hardware verification. Throttle suppresses URB resubmission only after the current callback, so one already-submitted packet may still arrive. Unidirectional mode depends on interrupt-out command delivery and exact byte count. The driver has no custom termios handling and no explicit write path.

## Test Signals
Test bidirectional and unidirectional product IDs, missing interrupt-out rejection for unidirectional mode, open/close commands and byte counts, interrupt read resubmission, throttle/unthrottle stop and restart, modem `TIOCMGET`/`TIOCMSET` behavior on hardware, disconnect during open error unwind, and MS7820 interface-class matching.
