# sources/distributed-fs/ceph-client/drivers/gpib/pc2/pc2_gpib.c

## Purpose
`pc2_gpib.c` implements Linux-GPIB support for PCII, PCIIa, PCIIa CB7210, and PCII/IIa compatible ISA GPIB boards. It is a thin board-specific wrapper around the shared NEC7210 core, responsible for ISA I/O region layout, IRQ handling, optional ISA DMA setup, interrupt-clear quirks, and registration of four board interface variants.

## Important APIs, types, and functions
The private board state is `struct pc2_priv`, embedding `struct nec7210_priv` plus IRQ and PCIIa interrupt-clear I/O address. Interrupt handlers are `pc2_interrupt()` and `pc2a_interrupt()`. Attach/detach paths include `pc2_generic_attach()`, `pc2_attach()`, `pc2_detach()`, `pc2a_common_attach()`, `pc2a_attach()`, `pc2a_cb7210_attach()`, `pc2_2a_attach()`, `pc2a_common_detach()`, `pc2a_detach()`, and `pc2_2a_detach()`. Most GPIB operation hooks are wrappers over NEC7210 helpers: `pc2_read()`, `pc2_write()`, `pc2_command()`, `pc2_take_control()`, `pc2_go_to_standby()`, `pc2_request_system_control()`, address, poll, EOS, status, and local-control helpers.

## Control flow
Module initialization registers four `gpib_interface` instances and unwinds previously registered ones if any registration fails. `pc2_attach()` allocates private state, configures NEC7210 I/O-port access with byte offset 1, requests an 8-port region at `config->ibbase`, resets the board, requests an IRQ if configured, registers a pseudo IRQ for polling ATN changes, writes the 8 MHz internal counter register, and brings the NEC7210 online. `pc2a_common_attach()` handles PCIIa-style sparse registers at offset `0x400`, validates base addresses and IRQ range, requests one port per register plus the IRQ-clear port, installs `pc2a_interrupt()`, clears pending interrupt state, resets, sets the clock, and goes online.

Interrupt handling is direct. PCII calls `nec7210_interrupt()` under `board->spinlock`. PCIIa reads ISR1/ISR2, clears the external interrupt circuit at `0x2f0 + irq`, and calls `nec7210_interrupt_have_status()`. Detach paths stop pseudo IRQs, free IRQs/DMA, reset hardware, release all requested regions, free coherent DMA buffers when compiled in, and free private state.

## State and persistence behavior
The driver keeps only in-memory runtime state in `struct pc2_priv` and the embedded NEC7210 state. Hardware state lives in ISA I/O registers. Optional DMA state is conditional on `PC2_DMA`, but the default path logs that DMA is disabled because the driver is not adapted to `isa_register_driver()` and lacks a `struct device`. There is no cross-boot persistence.

## Dependencies and integration points
The file depends on Linux I/O port, IRQ, DMA, spinlock, module, and Linux-GPIB infrastructure plus `nec7210.h`. It integrates with the GPIB core through `gpib_register_driver()` and delegates bus protocol behavior to NEC7210 library functions. Configuration comes from `struct gpib_board_config` fields such as `ibbase`, `ibirq`, and `ibdma`.

## Risks and edge cases
Several attach error paths return after region/IRQ/private allocation without a centralized cleanup call, so partial failures can leak resources until module removal or retry. PCIIa accepts only four hard-coded base addresses and IRQ 2 through 7. The PCIIa sparse region uses multiple one-byte `request_region()` calls, increasing cleanup complexity. The pseudo IRQ always uses `pc2_interrupt()` even in `pc2a_common_attach()`, which is worth regression testing because the real IRQ handler differs. DMA support is effectively disabled in normal builds.

## Test signals
Build coverage for all four interfaces, attach/detach with valid and invalid PCIIa base/IRQ values, IRQ delivery for both PCII and PCIIa clear-register behavior, pseudo IRQ polling for ATN, NEC7210 read/write/command/status operations, resource-failure injection in attach, and repeated attach/detach cycles are the main signals.
