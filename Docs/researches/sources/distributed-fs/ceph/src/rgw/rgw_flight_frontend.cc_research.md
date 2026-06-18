# sources/distributed-fs/ceph/src/rgw/rgw_flight_frontend.cc

## Purpose
Implements the RGW frontend wrapper for Arrow Flight and a GET object filter that detects Parquet schema metadata while normal GET responses flow through RGW.

## Important APIs, Types, And Functions
`null_flight_key` is defined as zero. `FlightFrontend` constructs/deletes `MemoryFlightStore` and `FlightServer`, initializes server location/options, starts `ServeAlt()` in a named thread, shuts down and joins. `FlightGetObj_Filter` buffers GET data to a temporary file, reads Parquet metadata on completion, and adds a `FlightData` entry.

## Control Flow
Frontend construction installs store/server pointers into `RGWProcessEnv`. `init()` chooses port 8077 by default, parses `grpc+tcp://localhost:<port>`, and initializes Arrow Flight options with client verification disabled. `run()` spawns the server thread. `stop()` calls `Shutdown()` and `Wait()`. The filter writes each data buffer to a temp file, and after expected object size is reached, opens the file with Arrow, reads Parquet metadata/schema, and registers a flight.

## State And Persistence Behavior
State is frontend-process local. Temporary files are created with `tmpnam`, removed in the destructor, and only used to discover schema/row metadata. Registered flights persist in memory until frontend teardown because store expiration is not implemented.

## Dependencies And Integration Points
Depends on Arrow Flight, Arrow file IO, Parquet metadata/schema conversion, RGW op filter chain, `req_state`, process env, and `rgw_flight.h`.

## Risks
The code contains a compile-time warning for `tmpnam`, which is insecure and race-prone. The filter writes the entire object to local disk before metadata extraction. Server binds localhost only and disables client verification. Pause/resume ignores config changes. Error handling for temp-file open failure is minimal.

## Test Signals
Tests should verify lifecycle init/run/stop/join, invalid port/location handling, Parquet GET filter registration, temp-file cleanup on success/failure, schema failure behavior for non-Parquet data, and concurrent GETs.
