# sources/distributed-fs/lizardfs/src/chunkserver/init.h

## Purpose
`init.h` defines the chunkserver module initialization order through three `run_tab` arrays. It is included by the generic server startup machinery to run early, normal, and late initialization functions with human-readable names.

## Important APIs, Types, and Functions
The file defines `typedef int (*runfn)(void)` and `struct run_tab { runfn fn; const char *name; }`. `RunTab` initializes the random generator, HDD space manager, main network server module, master connection module, and charts. `LateRunTab` starts master connection threads, HDD space manager threads, and network worker threads. `EarlyRunTab` is currently empty except for its sentinel.

## Control Flow
Normal initialization runs `rnd_init`, `hdd_init`, `mainNetworkThreadInit`, `masterconn_init`, and `chartsdata_init`. The comment notes that main network initialization must precede master connection so registration can advertise the listening address. Late initialization then creates job pools/background threads for master, HDD, and network serving.

## State and Persistence Behavior
This file stores only static initialization tables. It indirectly controls persistent behavior by ensuring HDD folders are parsed and scanned before threads begin and by registering event-loop destructors/reload hooks in the initialized modules.

## Dependencies and Integration Points
Includes pull in charts, HDD manager, master connection, network main thread, and random initialization. The arrays are consumed by the chunkserver's process bootstrap code outside this file.

## Risks and Edge Cases
Ordering is the key risk. Moving `masterconn_init` before `mainNetworkThreadInit` can break registration address reporting. Starting late threads before normal init finishes can expose uninitialized globals or missing event-loop hooks. The arrays use a null function sentinel, so consumers must stop on `(runfn)0`.

## Test Signals
Startup/integration tests should assert initialization order, successful registration after network listen setup, and clean shutdown after all modules register destructors. A compile-time or small runtime test can verify each table remains sentinel-terminated.
