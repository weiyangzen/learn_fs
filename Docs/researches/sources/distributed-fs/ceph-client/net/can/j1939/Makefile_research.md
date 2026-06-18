# sources/distributed-fs/ceph-client/net/can/j1939/Makefile

## Purpose
This Makefile defines how the SAE J1939 protocol implementation is built.

## Important APIs, Types, And Functions
`obj-$(CONFIG_CAN_J1939) += can-j1939.o` builds one composite object controlled by the Kconfig symbol. `can-j1939-objs` is composed from `address-claim.o`, `bus.o`, `main.o`, `socket.o`, and `transport.o`.

## Control Flow
When `CONFIG_CAN_J1939` is built in or modular, kbuild compiles the listed objects and links them into the `can-j1939` module or built-in object. `transport.o` is not in this research subset but is part of the final linked protocol.

## State And Persistence
The Makefile has no runtime state. It defines object composition, which determines which internal symbols from `j1939-priv.h` are available within the composite module.

## Dependencies And Integration Points
It integrates with the parent CAN networking build and the Kconfig symbol from `Kconfig`. Runtime integration is provided by `main.o` registering the protocol and netdevice notifier.

## Risks And Edge Cases
The private header declares transport functions implemented by `transport.o`; omitting that object would break J1939 send/receive. Any source-file addition must be reflected here to participate in the composite module.

## Test Signals
Build tests for `CONFIG_CAN_J1939=y` and `m` are sufficient for this file, with link coverage ensuring all private cross-file symbols resolve.
