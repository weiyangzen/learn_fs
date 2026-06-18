# sources/distributed-fs/ceph-client/arch/mips/cavium-octeon/executive/cvmx-pko.c

## Purpose
Initializes and configures PKO packet output hardware: command buffers, queue/port maps, enable/disable/reset, shutdown, and rate limiting.

## Important APIs, Types, And Functions
Public APIs are `cvmx_pko_initialize_global()`, `cvmx_pko_enable()`, `cvmx_pko_disable()`, `cvmx_pko_shutdown()`, `cvmx_pko_config_port()`, `cvmx_pko_rate_limit_packets()`, and `cvmx_pko_rate_limit_bits()`.

## Control Flow
Global init programs command-buffer pool/size, performs chip-specific mapping, and optimizes queue memory. Port config validates ranges and static-priority layout, initializes command queues, converts priorities to QoS masks, and writes queue pointer CSRs. Shutdown disables PKO, invalidates all queue mappings, shuts queues down, and resets the unit.

## State, Persistence, And Dependencies
State is in PKO CSRs plus command queue bootmem/FPA buffers. It depends on command queues, FPA output pools, helper interface mappings, and CPU clock.

## Integration Points
`cvmx-helper.c` initializes PKO and configures per-port queues, then enables PKO after input/interface setup. RGMII link changes temporarily manipulate PKO QoS.

## Risks
PKO should be disabled for configuration and drained for shutdown. Rate-limit functions do not guard division by zero. CN68XX uses a distinct iport path.

## Test Signals
Check queue mappings, invalid priority errors, packet output, shutdown on empty queues, CN68XX iport maps, and measured rate limits.
