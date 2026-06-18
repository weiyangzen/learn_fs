# sources/distributed-fs/ceph-client/drivers/slimbus/slimbus.h

## Purpose
This private SLIMbus core header defines message encodings, scheduler state, stream/channel/port state machines, controller internals, and internal core function prototypes shared by the SLIMbus core and controller drivers.

## Important APIs, Types, And Functions
It defines message constants for management, data-channel, reconfiguration, destination type, clock pause, and header extraction. Major types include `struct slim_framer`, `struct slim_msg_txn`, `struct slim_sched`, `struct slim_channel`, `struct slim_port`, `struct slim_stream_runtime`, and `struct slim_controller`. Transaction helper macros construct logical, broadcast, and enumeration destination messages. Inline helpers `slim_tid_txn()` and `slim_ec_txn()` classify messages needing transaction IDs or element codes.

## Control Flow
This file has no runtime flow, but it establishes the control contracts used elsewhere. Stream lifecycle moves channels from allocated to associated, defined, content-defined, active, removed, or disconnected. Port state moves disconnected, unconfigured, configured. The controller callback table defines how core transfer, address assignment, address lookup, stream enable/disable, and wakeup requests flow into hardware drivers.

## State, Persistence, And Dependencies
All defined state is in kernel memory owned by SLIMbus devices, controllers, and stream runtimes. There is no filesystem persistence. Dependencies include public `linux/slimbus.h`, driver model devices, IDA/IDR users from controller implementation, completions, mutexes, and list management.

## Integration Points
The header is consumed by SLIMbus core files and hardware drivers such as the Qualcomm NGD controller. Public exported functions such as `slim_register_controller()`, `slim_do_transfer()`, and stream helpers rely on these internal structures.

## Risks
This is a central ABI-like internal contract. Field layout and enum semantics must stay synchronized with the core, controller drivers, and stream code. Duplicate definition of `SLIM_CL_PER_SUPERFRAME` is harmless but noisy. Incorrect message length or destination encoding here propagates to all controllers.

## Test Signals
Signals are compile coverage for all SLIMbus users, controller registration, transaction ID allocation and response matching, stream lifecycle tests, and functional message transfer across supported controller drivers.
