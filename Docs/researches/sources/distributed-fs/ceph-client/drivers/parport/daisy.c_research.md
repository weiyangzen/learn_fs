# sources/distributed-fs/ceph-client/drivers/parport/daisy.c

## Purpose
`daisy.c` implements IEEE 1284.3 daisy-chain and multiplexor discovery for parport. It builds a canonical device-number topology, creates cloned `struct parport` aliases for mux ports, selects daisy devices for negotiated transfer modes, and provides `parport_open()`/`parport_close()` by canonical device number.

## Important APIs, Types, and Functions
The key state type is `struct daisydev`, linked in the global `topology` list protected by `topology_lock`. `parport_daisy_init()` discovers muxes and daisy devices, `parport_daisy_fini()` removes topology entries for a physical port, `parport_open()` registers a parport device by discovered canonical number, and `parport_daisy_select()` sends the correct chain-select command for EPP, ECP, or compatibility modes. Low-level command helpers are `cpp_daisy()` and `cpp_mux()`.

## Control Flow
Discovery registers a private `daisy_driver` once, checks whether a mux is present, clones extra logical ports for 2-way or 4-way muxes, recursively initializes clones, selects mux ports, deselects daisy devices, assigns daisy addresses, and adds a final legacy device entry. If nothing responds, it resets the attached devices through control lines and retries once. Address assignment uses the 1284.3 command preamble, strobes daisy addresses 0-3, records devices, and probes their device IDs.

## State and Persistence
State is in the in-memory topology list, `numdevs`, `daisy_init_done`, `port->muxport`, `real->slaves[]`, and `dev->daisy`. No persistent storage exists. Topology is rebuilt and removed as ports are announced or removed.

## Dependencies and Integration Points
The code depends on core parport registration, `parport_device_id()`, IEEE 1284 constants, parport control/status operations, scheduler/signal handling, and the daisy driver registration path. It integrates with high-level drivers through canonical device numbers and `parport_register_dev_model()`.

## Risks
Topology numbering can develop gaps; the comment notes enumeration is imperfect. `clone_parport()` creates aliases sharing the same physical registers, so mux selection must be correct before transfers. Discovery performs timing-sensitive control/data strobes and can mis-detect non-compliant peripherals. `add_dev()` silently drops entries on allocation failure.

## Test Signals
Expected logs include mux port announcements and daisy device counts. Tests should verify device-ID readback, `parport_open()` failure for absent devices, cleanup by `parport_daisy_fini()`, and correct select commands for EPP/ECP/compat modes on hardware or instrumented parport mocks.
