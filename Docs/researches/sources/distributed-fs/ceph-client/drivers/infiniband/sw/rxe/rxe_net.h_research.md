# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe_net.h

## Purpose

`rxe_net.h` declares RXE network lifecycle operations implemented in `rxe_net.c`. It is the small public boundary between RXE setup code and the RoCEv2 UDP/IP transport.

## Important APIs, Types, and Functions

It declares `rxe_net_add()`, `rxe_net_del()`, `rxe_register_notifier()`, `rxe_net_init()`, and `rxe_net_exit()`. These functions create RXE devices, manage per-netns tunnel sockets, and register/unregister netdev event handling.

## Control Flow

RXE module or device setup includes this header to initialize networking, create an RXE instance for a backing netdev, and subscribe to netdevice events. Teardown calls the paired delete/exit routines.

## State and Persistence Behavior

The header owns no state. Its functions manipulate RXE device state, per-netns sockets, and notifier registration in the implementation file.

## Dependencies and Integration Points

The declarations depend on kernel socket, IPv6 interface, module, netdev, and RDMA device types through the surrounding include graph. It integrates RXE core setup with transport initialization.

## Risks and Edge Cases

Call ordering matters: tunnel setup must precede traffic, notifier teardown must happen before module removal finishes, and `rxe_net_del()` must be balanced with device unregister. Reuse outside current include order may need explicit forward declarations.

## Test Signals

Build RXE module init/exit paths and run `rdma link add/delete` plus module unload to confirm balanced calls.
