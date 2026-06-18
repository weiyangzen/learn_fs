# sources/distributed-fs/ceph-client/net/can/j1939/Kconfig

## Purpose
This Kconfig file declares the `CAN_J1939` build option for in-kernel SAE J1939 protocol support over PF_CAN.

## Important APIs, Types, And Functions
The single symbol is `config CAN_J1939`, a tristate option named "SAE J1939". It depends on `CAN` and enables the J1939 socket type and protocol implementation.

The help text identifies the relevant standard areas: SAE J1939-21 for datalink/transport protocol and SAE J1939-81 for network management.

## Control Flow
Kconfig selection controls whether the J1939 objects in the sibling Makefile are omitted, built in, or built as a module. When enabled as a module, `main.c` advertises `MODULE_ALIAS("can-proto-" __stringify(CAN_J1939))`, allowing PF_CAN protocol autoload.

## State And Persistence
The file does not define runtime state. It controls compile-time availability and module/built-in linkage.

## Dependencies And Integration Points
The option depends on the broader CAN subsystem. It integrates with the net/can build hierarchy through the J1939 Makefile and with PF_CAN protocol registration at runtime.

## Risks And Edge Cases
Because this is a protocol-family extension, disabling it removes the `CAN_J1939` socket protocol even if user-space tools exist. As a module, correct aliasing and module autoload are important for `socket(PF_CAN, SOCK_DGRAM, CAN_J1939)`.

## Test Signals
Configuration tests should verify `CAN_J1939=n` omits the module, `m` builds `can-j1939.ko` with the expected alias, and `y` links the protocol into the kernel when `CAN` is enabled.
