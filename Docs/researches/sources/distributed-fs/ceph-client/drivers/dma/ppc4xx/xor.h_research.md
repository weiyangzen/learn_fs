# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/xor.h Research

## Purpose
`xor.h` describes the PPC440SPe XOR accelerator command block and register layout. It supports the XOR engine portion of the ADMA driver, including linked command blocks, completion interrupts, error status, refetch, and up to 16 operands per command.

## Important APIs, Types, and Functions
There are no functions. Constants define one XOR engine, the maximum operand count, command block control bits (`LNK`, `TGT`, `CBCE`, result-not-zero enable, XNOR), operand-count mask, status bits, control set/reset bits, and interrupt-enable bits.

`struct xor_cb` is the packed hardware command block. It contains control, byte count, status, target address, link address, and sixteen packed operand high/low address entries. `struct xor_regs` maps operand address registers, command block control/status/target/link registers, control set/reset registers, current command block address, PLB config, interrupt enable, parity error count, status, and revision ID.

## Control Flow
`adma.c` allocates coherent `struct xor_cb` objects from the device descriptor pool. XOR prepare functions set `cbc`, `cbbc`, target address, operands, and optional completion interrupt bits. Submit and append flows link command blocks using `cblal`/`cblah`, program the first command block address into `cblalr`/`cblahr`, and start or refetch the engine using `XOR_CRSR_XAE_BIT` and `XOR_CRSR_RCBE_BIT`. IRQ handling reads and clears `sr`, retries read-timeout cases by resubmitting the current address, and appends pending software-linked command blocks when the core becomes idle.

## State and Persistence
State exists in coherent command block memory and in the XOR MMIO register file. The current command block address and status register persist until hardware advances or software clears/resets them. No filesystem state is involved.

## Dependencies and Integration Points
The header depends on Linux types and is included by `adma.h`. It integrates with dmaengine through `adma.c` and with the `amcc,xor-accelerator` device tree node. Its packed layouts are hardware ABI, not normal C-only data structures.

## Risks and Edge Cases
Packed structure layout must remain byte-accurate. Operand count is limited to 16, so `adma.c` must split larger XOR operations into multiple slots. Link handling is sensitive because the driver may update software `hw_next` links before hardware link bits are patched. Error bits for invalid command blocks, invalid commands, parity, and read PLB timeout need clear handling to avoid stuck chains.

## Test Signals
Signals include successful XOR engine probe/reset, dmaengine XOR tests with more and fewer than 16 sources, command block completion interrupts, linked-list refetch under queued traffic, and error-path logging if invalid CB or timeout bits are injected or observed.
