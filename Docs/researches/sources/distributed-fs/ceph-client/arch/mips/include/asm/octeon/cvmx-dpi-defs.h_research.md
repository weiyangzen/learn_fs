# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-dpi-defs.h

## Purpose
This header defines Octeon DPI DMA/PCIe interface CSRs. It covers DMA engine control, doorbells, instruction buffers, request banks, interrupt/error handling, SLI port configuration, per-port error capture, and DMA request accounting.

## Important APIs, Types, and Functions
Address macros include `CVMX_DPI_CTL`, `DMA_CONTROL`, `REQ_GBL_EN`, request error response/reset controls, packet error response, `INT_REG`/`INT_EN`, per-engine enable/buffer/count/doorbell/in-flight/next-address/request-bank registers, per-PP counts, NCB config, info and PINT info, SLI port config/error/info, and BIST. `CVMX_DPI_SLI_PRTX_ERR()` is an inline address helper with chip/pass-specific address selection. Unions describe enable/clock control, DMA counts and doorbells, instruction buffer start/size/idle, next address, request-bank state, DMA engine enable, error response status, interrupt summary/enables, PCIe MPS/MRRS/MOLR/QLM/halt config, and SLI error address/info.

## Control Flow
There is no driver logic in the file. DMA drivers program engine buffers and request controls, ring doorbells, poll or handle interrupts, and inspect error CSRs. The SLI error address helper switches by `cvmx_get_octeon_family()` and CN68XX pass to return the correct CSR address.

## State and Persistence Behavior
DPI CSRs hold DMA engine configuration, pending work counts, in-flight counts, doorbell state, error response policy, interrupt pending/enables, and PCIe port parameters. These persist in hardware until reset or reconfiguration; error registers may latch fault addresses and request metadata.

## Dependencies and Integration Points
It depends on Octeon model/family helpers and CSR address mapping. It integrates with DMA engine drivers, PCIe/SLI setup, interrupt handling, error reporting, and hardware command queues that feed DMA engines.

## Risks
Chip-specific SLI error offsets are easy to misselect, especially CN68XX pass 1 versus pass 2. Doorbell and count fields are hardware-synchronized; bad sequencing can lose DMA work or overrun instruction buffers. Error response/reset enable bits control whether faults are reported or reset, so overly broad writes can mask or amplify DMA failures.

## Test Signals
Exercise DMA transfers on every enabled engine, buffer-boundary and doorbell-count stress, PCIe error injection or fault reporting, SLI port config validation, interrupt enable/clear behavior, and family-specific tests for CN61XX/CN63XX/CN66XX/CN68XX/CNF71XX.
