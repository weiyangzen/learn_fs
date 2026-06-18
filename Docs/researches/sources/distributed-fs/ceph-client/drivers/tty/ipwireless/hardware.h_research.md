# sources/distributed-fs/ceph-client/drivers/tty/ipwireless/hardware.h

## Purpose
`hardware.h` declares the public interface from the IPWireless hardware engine to the rest of the driver. It hides `struct ipw_hardware` internals and exposes lifecycle, interrupt, transmit, modem-control, network association, and version-specific initialization entry points.

## Important APIs, Types, and Functions
The header defines modem-control bit masks: `IPW_CONTROL_LINE_CTS`, `DCD`, `DSR`, `RI`, `DTR`, and `RTS`. It forward-declares `struct ipw_hardware` and `struct ipw_network`.

The exported functions are `ipwireless_hardware_create()`, `ipwireless_hardware_free()`, `ipwireless_interrupt()`, `ipwireless_set_DTR()`, `ipwireless_set_RTS()`, `ipwireless_send_packet()`, `ipwireless_associate_network()`, `ipwireless_stop_interrupts()`, `ipwireless_init_hardware_v1()`, `ipwireless_init_hardware_v2_v3()`, and `ipwireless_sleep()`.

## Control Flow
Higher layers allocate hardware state, initialize it for a card version with I/O/memory mappings and reboot callback, associate a network object, request IRQs using `ipwireless_interrupt()`, and then send data/control-line changes through this API. Teardown calls `ipwireless_stop_interrupts()` before freeing or disconnecting upper layers.

## State and Persistence Behavior
The header exposes no structure fields. State is owned by the opaque `ipw_hardware` implementation in `hardware.c`.

## Dependencies and Integration Points
It depends on kernel types, scheduler declarations, and interrupt return types. It is consumed by IPWireless main/network/tty code and implemented by `hardware.c`.

## Risks and Edge Cases
Callers must honor context expectations: `ipwireless_stop_interrupts()` must run in process context, send/control functions can allocate and queue work, and the IRQ handler expects a device object whose hardware pointer remains valid. Channel indices must correspond to `NO_OF_IPW_CHANNELS` used internally.

## Test Signals
Signals include successful compile-time linkage with the other IPWireless objects, correct modem-control bit propagation to tty/network layers, packet-sent callbacks from `ipwireless_send_packet()`, and teardown without IRQ/work callbacks after stop/free.
