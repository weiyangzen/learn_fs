<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipaq.c -->
# sources/distributed-fs/ceph-client/drivers/usb/serial/ipaq.c

## Purpose
Implements a USB serial driver for many PocketPC, Windows Mobile, Smartphone, iPAQ, and related PDA sync devices. The driver presents a single tty-style serial port over bulk endpoints and sends a vendor/control setup message required by these devices before using the generic usb-serial data path.

## Important APIs, Types, And Functions
The large `ipaq_id_table` is the main device binding surface, covering many vendor/product pairs. `ipaq_device` is the single `usb_serial_driver` with 256-byte bulk in/out buffers, custom `.open`, `.attach`, and `.calc_num_ports`, and generic usb-serial behavior for the rest. `ipaq_open()` performs optional startup delay, repeatedly sends a class/vendor-style control message `bRequest=0x22`, `bmRequestType=0x21`, `wValue=1`, then calls `usb_serial_generic_open()`. `ipaq_calc_num_ports()` validates endpoint availability and chooses which bulk endpoint pair to expose. `ipaq_startup()` validates the active configuration and resets the USB configuration.

## Control Flow
On probe, usb-serial matches one of the listed IDs, calls `ipaq_calc_num_ports()` to reject obviously wrong composite interfaces, optionally switches to the second bulk in/out pair for devices exposing multiple pairs, and forces the interface to one bulk-in and one bulk-out port. Attach checks that the active configuration value is 1 and calls `usb_reset_configuration()`. Open sleeps for `initial_wait` seconds if configured, then retries the setup control message up to `connect_retries`, sleeping one second between failures. Once a control message succeeds, the generic open path submits read URBs and enables normal tty I/O.

## State And Persistence
The driver owns no per-port private structure. Runtime behavior is controlled by module parameters `connect_retries` and `initial_wait`. USB configuration reset may alter device runtime state, but no persistent device storage is changed.

## Dependencies And Integration Points
It depends on the usb-serial core, generic usb-serial open/read/write implementation, tty layer, and USB core control messaging. It is a compatibility driver for sync protocols layered in userspace over the exposed tty.

## Risks And Edge Cases
The huge static ID table can bind composite devices where only some interfaces are suitable; endpoint filtering is intentionally simple. Devices with non-1 configuration values are rejected except for a FIXME note about HP rx3715-like devices. `ipaq_open()` treats exhausting retries carefully, but if the last retry succeeds when `retries` reaches zero it still proceeds because `result` is zero. The control message semantics are empirical from Windows sniffing, so unusual firmware may need different setup.

## Test Signals
Test signals include binding only to interfaces with bulk in/out endpoints, selecting the correct second endpoint pair on four-endpoint devices, successful control-message retry behavior, `usb_reset_configuration()` success during attach, generic tty data transfer after open, and module-parameter tests for delay and retry limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/serial/ipaq.c -->
