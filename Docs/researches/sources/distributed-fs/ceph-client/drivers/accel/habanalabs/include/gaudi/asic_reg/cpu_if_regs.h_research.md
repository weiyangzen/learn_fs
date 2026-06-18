# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/cpu_if_regs.h

## Purpose

`cpu_if_regs.h` is an auto-generated Gaudi CPU interface register map. It gives symbolic names to MMIO offsets under the CPU_IF block so driver code can configure host/firmware queues, AXI attributes, counters, and interrupt/status registers without embedding raw addresses.

## Important APIs, Types, and Constants

The header exports only `#define` constants. Major groups are AXI/user override registers (`mmCPU_IF_ARUSER_OVR`, `AWUSER_OVR`, `AXCACHE_OVR`, `LOCK_OVR`, `PROT_OVR` and enable controls), outstanding and response controls (`MAX_OUTSTANDING`, `EARLY_BRESP_EN`, `FORCE_RSP_OK`, `CPU_MSB_ADDR`), queue interface registers (`PF_PQ_PI`, PQ/CQ/EQ base low/high, lengths, EQ read offset, and `QUEUE_INIT`), and error/interrupt groups for TPC, DMA, SRAM, NIC, DMA_IF, HBM, PLL, and SEI paths.

## Control Flow

The header has no runtime control flow. It is consumed by Gaudi initialization code. CPU bring-up writes `mmCPU_IF_CPU_MSB_ADDR` when firmware security does not own that setting. CPU queue initialization writes PQ, EQ, and CQ base addresses, queue lengths, EQ read offset, PF PQ producer index, and `mmCPU_IF_QUEUE_INIT`, then polls `QUEUE_INIT` until firmware reports host readiness. Runtime event handling updates `mmCPU_IF_EQ_RD_OFFS` as the event queue consumer index advances.

## State and Persistence Behavior

The constants map to hardware registers that persist until reset or reinitialization. The queue base/length registers define shared-memory queue placement, `PF_PQ_PI` is mutable queue producer state, and `EQ_RD_OFFS` is mutable event-queue consumer state. Interrupt status/mask/clear registers hold fault and error state for multiple hardware blocks. The header itself holds no software state.

## Dependencies and Integration Points

This generated file is included by Gaudi driver code through the ASIC register include set. It integrates with firmware loader data (`cpu_dyn_regs`), queue allocation (`hdev->kernel_queues`, `hdev->event_queue`, and CPU-accessible memory), and GIC/MSI interrupt setup. It also sits next to mask headers that define bit positions for related control/status registers.

## Risks

Generated register maps are high blast-radius dependencies: an incorrect address silently redirects MMIO writes. Queue base/length mistakes can make firmware read or write the wrong memory, while wrong interrupt status or clear addresses can mask real hardware faults. Security-sensitive override registers can alter AXI attributes and protection behavior, so writes to those registers must be tightly controlled by initialization policy.

## Test Signals

Strong signals include successful CPU firmware initialization, `QUEUE_INIT` reaching the ready-for-host state within timeout, working command and event queues, correct PI-update interrupt delivery, and no spurious ECC/SEI interrupt storms. Register readback tests in simulation or bring-up should confirm all queue base/length registers and `CPU_MSB_ADDR` match expected DMA addresses.
