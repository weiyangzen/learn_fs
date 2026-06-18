# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.h

## Purpose
This header defines the callback interface and attach function for the AS102 DVB-T frontend shim.

## Important APIs And Types
`struct as102_fe_ops` provides parent-supplied callbacks: `set_tune`, `get_tps`, `get_status`, `get_stats`, and `stream_ctrl`. `as102_attach()` takes a frontend name, ops table, private parent pointer, and eLNA config, returning a `struct dvb_frontend *`.

## Control Flow And Integration
The AS102 transport/USB driver calls `as102_attach()` and implements the callback table using its command protocol. The frontend file translates standard DVB operations into these callbacks.

## State And Persistence
This header declares only contracts. Runtime state is allocated in `as102_fe.c` and stores the callback pointers and private context.

## Dependencies
The header includes AS10x packed command/status types from `as102_fe_types.h` and relies on DVB frontend declarations being available through implementation includes.

## Risks
The callback table is not optional in the implementation; missing functions will crash when frontend ops are invoked. ABI-like packed structs must stay synchronized with firmware/control-protocol expectations.

## Test Signals
Compile checks should catch callback signature mismatches. Runtime tests should confirm all callbacks are called with the expected private pointer and arguments.
