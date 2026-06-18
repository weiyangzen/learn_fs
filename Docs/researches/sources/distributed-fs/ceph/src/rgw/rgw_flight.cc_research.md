# sources/distributed-fs/ceph/src/rgw/rgw_flight.cc

## Purpose
Implements RGW's experimental Arrow Flight server. It registers Parquet object metadata as Flights and serves selected objects through Arrow Flight `DoGet` by reading RGW objects through SAL and converting Parquet to Arrow record batches.

## Important APIs, Types, And Functions
`FlightKeyToTicket()` and `TicketToFlightKey()` translate between internal keys and Flight tickets. `FlightData` stores object identity, schema, metadata, row/object sizes, and temporary user id. `MemoryFlightStore` provides in-memory keyed storage. `FlightServer` implements `ListFlights()` and `DoGet()`; `GetFlightInfo()` and `GetSchema()` are placeholders. Local classes `OwnedBuffer` and `RandomAccessObject` adapt RGW object reads to Arrow IO.

## Control Flow
`ListFlights()` returns a custom listing that iterates `FlightStore::after_key()` and builds `FlightInfo` descriptors from tenant, bucket, object key parts, endpoints, schema, row count, and object size. `DoGet()` parses the ticket, looks up `FlightData`, loads the RGW bucket, gets the object, wraps it in `RandomAccessObject`, opens a Parquet reader, reads the full table, converts the table to record batches, and returns a `RecordBatchStream`.

## State And Persistence Behavior
Flights are process-local only. `next_flight_key` is atomic but monotonic and not persisted. `MemoryFlightStore::remove_flight()` and `expire_flights()` are stubs, so entries accumulate for the lifetime of the frontend. `RandomAccessObject` owns a SAL read op and tracks current position/closed state.

## Dependencies And Integration Points
Depends on Arrow, Arrow Flight, Parquet Arrow reader, RGW SAL driver/bucket/object APIs, and Flight metadata produced by `FlightGetObj_Filter` in the frontend file.

## Risks
`GetFlightInfo()` and `GetSchema()` return OK without data. `DoGet()` reads an entire Parquet table into memory before streaming batches. Error paths after bucket load failures are incomplete. Authorization is TODO and user id is only carried as a placeholder. `MemoryFlightStore` returns copies of `FlightData`, and expiration/removal are unimplemented.

## Test Signals
Tests should cover ticket parse errors, missing flight keys, listing order, DoGet on valid Parquet objects, bucket/object load failures, partial/short reads, Parquet metadata compatibility, large object memory usage, and concurrent add/list/get.
