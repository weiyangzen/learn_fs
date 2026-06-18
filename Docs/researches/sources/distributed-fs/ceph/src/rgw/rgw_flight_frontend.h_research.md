# sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.h

## Purpose
Declares the Arrow Flight frontend and GET filter types that plug Flight support into RGW's frontend/process environment.

## Important APIs, Types, And Functions
`FlightKey` is a `uint32_t`, with `null_flight_key` defined externally. `FlightFrontend` implements `RGWFrontend` methods for lifecycle management. `FlightGetObj_Filter` derives from `RGWGetObj_Filter` and overrides `handle_data()`.

## Control Flow
The frontend is configured and owned like other RGW frontends. The filter is intended to be inserted into object GET response pipelines so data can be observed, metadata extracted, and then forwarded to the next filter.

## State And Persistence Behavior
`FlightFrontend` owns a server thread and references process env. `FlightGetObj_Filter` tracks offsets, expected size, object identity, temp-file stream/name, schema status, and user id for eventual `FlightData` creation.

## Dependencies And Integration Points
Includes `rgw_frontend.h`, `rgw_op.h`, Arrow status, and common forward/thread definitions. Integrates with `RGWProcessEnv` fields `flight_store` and `flight_server`.

## Risks
The filter stores a const reference to process env and an ofstream, so destruction order and filter lifetime matter. Auth is marked TODO. Namespace and object instance handling are noted as incomplete.

## Test Signals
Compile-time tests should ensure frontend polymorphism and filter chaining. Runtime tests should verify handle_data forwards data and registers flights only after complete objects.
