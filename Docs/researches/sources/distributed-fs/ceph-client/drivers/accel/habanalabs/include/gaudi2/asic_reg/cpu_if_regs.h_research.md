<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/cpu_if_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/cpu_if_regs.h

## Purpose
`cpu_if_regs.h` is the generated Gaudi2 CPU interface register map, prototype `CPU_IF`. It exposes 377 `mmCPU_IF_*` address macros in the 0x4CC1104-0x4CC19D8 range for CPU-originated AXI attribute overrides, host/firmware queues, address MSB configuration, interrupt aggregation, ECC/error reporting, SPI/SEI/MSI-X routing, counters, and low-bandwidth termination diagnostics.

## Important APIs, types, and functions
The file exports constants only. Important groups include CPU AXUSER/AWCACHE/LOCK/PROT override and override-enable registers; max outstanding, early response, and force-response controls; CPU SEI status/clear/mask; write/read total and inflight counters; SRAM/CFG/HBM/PCIe MSB address registers; KMD dirty status; master-interface E2E controls; LBW terminate address/response diagnostics; PF persistent/completion/event queue base/length/init registers; per-engine SERR/DERR/SEI/SPI status-clear-mask sets for TPC, MME, HDMA, PDMA, SRAM, HBM, HMMU, DEC, NIC, sync manager, HIF, XBAR, PLL, and PCIe; and MSI-X busy/generation registers.

## Control flow
There is no executable code. Device initialization programs address-extension registers and queue base/length pairs, initializes CPU-visible queues with `QUEUE_INIT`, unmasks the interrupt classes it expects to handle, and configures AXI overrides if needed. Interrupt handling reads status registers, writes clear registers, and uses masks to suppress or enable classes. Recovery code reads termination/error address registers, dirty status, counters, and inflight counts to decide whether firmware, queues, or the whole device must be reset.

## State and persistence behavior
The CPU interface is a central persistent hardware state bank. Queue bases and lengths persist while firmware and kernel queues are active. Interrupt masks persist until explicitly changed, while status/clear registers expose latched event state. Address MSB and AXI override registers affect subsequent CPU interface transactions, so stale values can corrupt address interpretation or transaction security/cache attributes.

## Dependencies and integration points
This header integrates with Gaudi2 firmware boot, CPU-CP queue setup, interrupt controller programming, MSI-X generation, ECC/SPI/SEI error handling, and low-level register access code. Consumers also depend on queue layout definitions and device address-map constants outside this generated header.

## Risks and edge cases
The highest risks are interrupt status/clear/mask triplet drift, programming queue base high/low words inconsistently, leaving interrupt masks wrong after reset, and misconfiguring address-extension registers for SRAM/CFG/HBM/PCIe windows. Because many status sets are replicated by engine family and index, a table off-by-one can acknowledge or mask the wrong hardware source.

## Test signals
Validation should include firmware queue initialization, event queue delivery, MSI-X generation, ECC/SPI/SEI interrupt injection for multiple engine families, reset with mask restoration, queue base/length boundary tests, and diagnostics showing read/write inflight counters return to zero during idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/cpu_if_regs.h -->
