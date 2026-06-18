# sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-ethernet.h

## Purpose
Primary shared header for the Octeon Ethernet driver, selecting real Octeon architecture headers or compile-test stubs and defining per-netdev private state.

## Important APIs, Types, And Functions
Defines `struct octeon_ethernet` with hardware port/queue/FAU, netdev pointer, interface mode, PHY mode, TX free lists, link state, poll callback, periodic work, and OF node. Declares common, mode-specific, TX/RX, carrier, and global driver symbols.

## Control Flow
All implementation files include this header to access CVMX types and shared driver APIs. `ethernet.c` allocates `struct octeon_ethernet` as netdev private data and mode files consume it.

## State And Persistence
The header defines runtime state shape but stores no data itself. Externs expose module-global state in `ethernet.c`.

## Dependencies And Integration Points
On real Octeon builds it includes many `<asm/octeon/cvmx-...>` headers. Under non-Octeon compile tests it includes `octeon-stubs.h`. It also integrates OF and phylib types.

## Risks
The compatibility boundary between real architecture headers and stubs is broad. Any missing CVMX declaration breaks compile-test or target builds. `struct octeon_ethernet` embeds fixed 16 TX QoS queues, matching assumptions in TX cleanup.

## Test Signals
Compile under `CONFIG_CAVIUM_OCTEON_SOC` and `COMPILE_TEST`, check all shared prototypes, and validate netdev private layout use across core/RX/TX/mode files.
