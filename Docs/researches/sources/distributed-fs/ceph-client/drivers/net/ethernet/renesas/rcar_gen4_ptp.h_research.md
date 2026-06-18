# sources/distributed-fs/ceph-client/drivers/net/ethernet/renesas/rcar_gen4_ptp.h

## Purpose
This header declares the public internal API for the shared Renesas R-Car Gen4 gPTP provider. It lets Ethernet drivers allocate/register/unregister a PHC context and query or read the clock without exposing the provider's private structure layout.

## Important APIs, Types, And Functions
- Forward declaration: `struct rcar_gen4_ptp_private` keeps provider state opaque to clients.
- Lifecycle: `rcar_gen4_ptp_alloc()`, `rcar_gen4_ptp_register()`, and `rcar_gen4_ptp_unregister()`.
- Query helpers: `rcar_gen4_ptp_clock_index()` returns the PHC index or `-1` when uninitialized, and `rcar_gen4_ptp_gettime64()` reads current time into a `timespec64`.

## Control Flow
Clients include this header, allocate a provider with a platform device and MMIO timer address, register it with the timer rate once hardware is ready, expose `rcar_gen4_ptp_clock_index()` through ethtool timestamp info, optionally read time for timestamp conversion, and unregister during hardware teardown.

## State And Persistence
The header defines no storage and no persistence. It intentionally hides provider state behind an opaque pointer. Runtime state is owned by `rcar_gen4_ptp.c` and client drivers store only the returned pointer.

## Dependencies And Integration Points
The declarations depend on kernel types from including translation units: `struct platform_device`, `void __iomem`, `u32`, and `struct timespec64`. It is included by `rcar_gen4_ptp.c`, `rswitch.h`, and client drivers that use the shared Gen4 PTP block. Kconfig/Makefile ensure `rcar_gen4_ptp.o` is available for R-Switch and RTSN.

## Risks And Edge Cases
- Because the header does not include type headers itself, includers must already have the needed kernel type declarations.
- Opaque-state design prevents clients from validating `initialized` directly; they must use return values such as `clock_index == -1`.
- Register/unregister ordering is left to clients, so incorrect lifecycle handling can still call helpers after teardown.

## Test Signals
Compile all includers, verify no missing type declarations under `COMPILE_TEST`, confirm modules link to exported functions, and test client remove paths call unregister after successful register.
