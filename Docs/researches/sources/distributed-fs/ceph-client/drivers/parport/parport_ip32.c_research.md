# sources/distributed-fs/ceph-client/drivers/parport/parport_ip32.c

## Purpose
`parport_ip32.c` is the SGI O2/IP32 built-in parallel-port driver for the memory-mapped TL16PIR552-compatible hardware behind MACE. It supports basic SPP/PS2, IRQ forwarding, hardware EPP, FIFO-backed compatibility/ECP writes, and optional DMA for FIFO writes.

## Important APIs, Types, and Functions
Key types are `struct parport_ip32_regs`, `struct parport_ip32_private`, and `struct parport_ip32_dma_data`. The operation table starts as `parport_ip32_ops` and is patched during probing to use hardware SPP/EPP/ECP paths when enabled. Major functional groups include DMA setup/interrupt/stop (`parport_ip32_dma_*`), interrupt forwarding/local completion (`parport_ip32_interrupt()`), DCR/ECR register helpers, EPP accessors, FIFO wait/write/drain/residue helpers, compatibility and ECP write accelerators, feature probing, and module init/exit.

## Control Flow
Initialization computes memory-mapped ISA-style register addresses with a register shift of 8, allocates ops/private data, registers a placeholder parport, verifies ECR presence, assumes base PCSPP/TRISTATE capability, probes FIFO depth and thresholds, requests the main parallel IRQ if enabled, registers DMA context IRQs if enabled, patches operation callbacks for selected hardware features, initializes PS2 forward mode, prints modes, and announces the port. Transfers then use the active parport mode: EPP functions switch to EPP mode, perform byte or string I/O, clear timeout on failure, and return to PS2; FIFO compatibility/ECP writes switch to PPF/ECP mode, wait for peripheral readiness, write through PIO or DMA, drain and account for residue, then reset back to PS2.

## State and Persistence
Per-port private state caches DCR, writable DCR bits, FIFO parameters, IRQ mode, and a completion used for local waits. DMA state is global because only one port is supported: mapped buffer address, remaining byte count, active context, IRQ-on flag, and spinlock. Module parameters `features` and `verbose_probing` control runtime feature enablement. No state persists beyond module lifetime.

## Dependencies and Integration Points
The driver depends on MIPS IP32 MACE registers/IRQs, DMA mapping APIs, parport core, generic IEEE 1284 operations, completions, spinlocks, and memory-mapped I/O helpers. It integrates hardware IRQs either by forwarding to `parport_irq_handler()` or satisfying local FIFO waits, and registers DMA context IRQs separately from the parport IRQ.

## Risks
The file documents unimplemented hardware ECP read and ECP address-write support. DMA supports only `DMA_TO_DEVICE` and uses `BUG_ON()` for other directions. FIFO status is noted as unreliable; residue accounting has a FIXME about a missing byte when the printer is offline. Feature probing mutates the global `features` mask, so one failed probe disables later feature paths. Correct behavior depends on IP32-only single-port assumptions and MACE context IRQ handling.

## Test Signals
Useful tests include boot/probe logs for ECR/FIFO/IRQ/DMA feature enablement, EPP timeout clearing, PIO and DMA FIFO write counts, IRQ-mode switching between forwarded and local completion behavior, module parameter combinations disabling each feature, cleanup of IRQ/DMA resources on unload, and real peripheral tests for SPP/EPP/ECP write paths.
