# sources/distributed-fs/ceph-client/drivers/staging/octeon/octeon-stubs.h

## Purpose
Compile-test shim that provides enough Octeon CVMX constants, types, unions, and inline functions to build the staging Ethernet driver on non-Octeon platforms.

## Important APIs, Types, And Functions
Defines IRQ/model/feature macros, FPA/FAU/GMX/PIP/POW/PKO constants, CVMX WQE and buffer pointer unions, link-info structures, many CSR union layouts, interface-mode enums, and no-op or dummy inline functions for FAU, scratch, FPA, helper, POW, SPI, PKO, and WQE operations.

## Control Flow
`octeon-ethernet.h` includes this file when `CONFIG_CAVIUM_OCTEON_SOC` is not set. The stubs return harmless zero/null values or no-op for hardware operations, allowing type checking and dead-code compile coverage but not real runtime behavior.

## State And Persistence
No real state. Inline functions do not model hardware; most return constants, null pointers, or their input value.

## Dependencies And Integration Points
Bridges Octeon-specific implementation files to generic kernel compile-test builds. It must track the subset of CVMX API and bitfields used by this driver.

## Risks
Because behavior is fake, compile-test can miss runtime ordering, counter, and null-pointer issues. Some stub return values such as zero queues or null FPA allocations can make accidental execution unsafe. Bitfield definitions must remain close enough to real headers for code to compile correctly.

## Test Signals
`COMPILE_TEST` builds on non-Octeon architectures, enabling optional netfilter/XFRM/VLAN variations. Runtime should not bind on non-Octeon hardware; target-hardware testing must use real CVMX headers.
