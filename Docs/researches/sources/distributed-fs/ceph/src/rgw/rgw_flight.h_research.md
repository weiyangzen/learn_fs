# sources/distributed-fs/ceph/src/rgw/rgw_flight.h

## Purpose
Declares the Arrow Flight data model, store abstraction, server class, and utility owning string view used by RGW Flight support.

## Important APIs, Types, And Functions
`FlightData` records a Flight key, URI, tenant/bucket/object identity, record and object counts, Arrow schema, Parquet key/value metadata, and user id. `FlightStore` abstracts add/get/iterate/remove/expire. `MemoryFlightStore` implements the abstraction with a mutex-protected map. `FlightServer` derives from `arrow::flight::FlightServerBase` and declares `ListFlights()`, `GetFlightInfo()`, `GetSchema()`, and `DoGet()`. `OwningStringView` owns a heap buffer while presenting `std::string_view`.

## Control Flow
The header's intended flow is: frontend creates `MemoryFlightStore` and `FlightServer`, GET filters add `FlightData`, and Arrow Flight RPCs use `FlightServer` methods to list or retrieve registered Flights.

## State And Persistence Behavior
The declared `lifespan` constant suggests planned expiry, but expiration is not enforced by this header's concrete implementation. Store contents are in-memory only.

## Dependencies And Integration Points
Includes Arrow type/Flight server headers, Ceph context/time/logging, `rgw_frontend.h`, and `rgw_flight_frontend.h` for `FlightKey`. `FlightServer` holds `RGWProcessEnv`, SAL driver pointer, `DoutPrefix`, and `FlightStore`.

## Risks
The header exposes raw `FlightStore*` ownership through `FlightServer`; frontend lifecycle must delete in the right order. `OwningStringView` inherits from `std::string_view`, which is unusual and demands care with moves and destructor ownership.

## Test Signals
Compile and unit tests should cover `OwningStringView::make()/shrink()`, store polymorphism, Flight server construction, and lifecycle with frontend teardown.
