# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.h

## Purpose
`cavium.h` is the shared private interface and register-definition header for Cavium OCTEON and ThunderX MMC/eMMC drivers. It defines the common host/slot structures, register offset macros, bitfield masks, command/response type helper structs, and exported shared-core prototypes used by both bus-specific front ends.

## Important APIs, Types, and Functions
`struct cvm_mmc_host` describes controller-wide state: device pointer, command and DMA register bases/offsets, cached config, clock frequency, current request, SG iterator, DMA mode flags, feature flags, IRQ lock/serializer, shared power GPIO/accounting, slot arrays, and callback hooks for power, bus locking, interrupt enabling, and DMA erratum handling. `struct cvm_mmc_slot` describes per-slot MMC state: `mmc_host`, parent host, cached clock, cached switch/RCA values, sample-delay counts, and bus id. `struct cvm_mmc_cr_type` and `struct cvm_mmc_cr_mods` support command/response type override calculation.

The header declares `cvm_mmc_interrupt`, `cvm_mmc_of_slot_probe`, `cvm_mmc_of_slot_remove`, and `cvm_mmc_irq_names`.

## Control Flow and State
The header itself has no executable flow, but its macros define how shared code computes addresses for `MIO_EMM_*` command, response, switch, watchdog, sample, buffer, and DMA registers. The `reg_off` and `reg_off_dma` fields allow the same macros to work for OCTEON and ThunderX layouts. Bitfield definitions describe command submission, DMA setup, response status, interrupt bits, switch configuration, FIFO commands, and DMA config.

## State and Persistence Behavior
No persistence is implemented. The structures define all volatile state that survives between callbacks while the driver is loaded: active request state, per-slot cached hardware settings, shared power user count, and feature flags. Callback fields are the abstraction boundary between common code and platform/PCI front ends.

## Dependencies and Integration Points
The header includes Linux bitops, clk, GPIO, IO, MMC host, OF, scatterlist, and semaphore headers. It is included by `cavium.c`, `cavium-octeon.c`, and `cavium-thunderx.c`. Its register macros are tightly coupled to Cavium MIO_EMM hardware documentation and to `FIELD_PREP`/`FIELD_GET` use in the implementation.

## Risks and Test Signals
Risks include mismatched offsets for a front end, incorrect bit masks causing silent hardware programming failures, callback fields left unset, and structure changes that break common/front-end contracts. Test signals are mostly compile- and integration-level: both OCTEON and ThunderX build, register offsets produce expected MMIO access on each platform, all exported prototypes match definitions, max slot count bounds are respected, and interrupt-name indexing matches requested IRQ vectors.
