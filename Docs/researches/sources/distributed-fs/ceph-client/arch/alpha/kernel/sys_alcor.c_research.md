# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_alcor.c

## Purpose
`sys_alcor.c` provides board support for Alpha Alcor and XLT systems. It implements GRU interrupt mask/ack logic, PCI interrupt dispatch and slot mapping, CIA PCI initialization with XLT detection, SRM reset behavior, and the `alpha_machine_vector` definitions for Alcor and XLT.

## Important APIs, Types, And Functions
- `cached_irq_mask` mirrors enabled GRU interrupt bits; unlike Cabriolet, mask bit true means enabled.
- `alcor_update_irq_hw()`, `alcor_enable_irq()`, `alcor_disable_irq()`, and `alcor_mask_and_ack_irq()` program GRU interrupt mask/clear registers.
- `alcor_isa_mask_and_ack_irq()` chains i8259A ack and clears the ISA summary bit in GRU.
- `alcor_irq_type` is the IRQ chip for platform IRQs 16-47.
- `alcor_device_interrupt()` reads `GRU_INT_REQ`, filters with `GRU_INT_REQ_BITS`, and dispatches either ISA cascade or `handle_irq(16 + bit)`.
- `alcor_init_irq()` initializes GRU registers, IRQ chips, i8259A, ISA DMA, and ISA cascade IRQ.
- `alcor_map_irq()` maps PCI IDSEL/pin combinations to IRQs using `COMMON_TABLE_LOOKUP`.
- `alcor_kill_arch()` chains CIA shutdown and, when SRM restore setup is not compiled in, can write `GRU_RESET` with `0x0000dead` for SRM restart.
- `alcor_init_pci()` calls `cia_init_pci()` and detects XLT-family motherboards by a built-in DEC Tulip at devfn 6.
- `alcor_mv` and `xlt_mv` define machine vectors.

## Control Flow
IRQ initialization optionally switches device interrupts to SRM dispatch when booted under SRM, clears and configures GRU masks/edge/polarity, installs level IRQ handlers except unconnected lines 36-46, overrides ISA ack, initializes ISA PIC/DMA, and requests the ISA cascade. Device interrupts loop over pending GRU bits, dispatching bit 31 to ISA and other bits to Linux IRQ numbers.

PCI init first performs CIA setup, then probes for a DEC Tulip in slot 6. Finding it changes `alpha_mv.sys.cia.gru_int_req_bits` to XLT request bits and logs AS500/XLT detection.

## State And Persistence
State includes `cached_irq_mask`, GRU hardware registers, i8259A ack hook, machine-vector system CIA bits, and registered IRQ descriptors. Hardware interrupt mask state persists until reset or reprogramming.

## Dependencies And Integration Points
The file depends on CIA core logic, GRU register definitions, common IRQ helpers, i8259A, ISA DMA, PCI device probing, SRM interrupt dispatch, and machine-vector macros. `setup.c` selects these vectors for Alcor/XLT variants.

## Risks
- GRU mask polarity differs from other platforms; confusing enabled/disabled semantics can invert interrupts.
- Lines 20-30 relative to PCI range are skipped to avoid spurious interrupts; enabling them during probing can misbehave.
- XLT detection depends on a DEC Tulip at a specific devfn.
- `alcor_kill_arch()` has conditional behavior depending on SRM restore compile options.

## Test Signals
- Alcor/XLT boot logs show correct vector and optional XLT Tulip detection.
- PCI interrupts route according to slot/pin table and ISA cascade works.
- IRQ masking/ack clears GRU state without interrupt storms.
- Restart under SRM behaves as expected for the board.
