# sources/distributed-fs/ceph-client/arch/alpha/kernel/sys_cabriolet.c

## Purpose
`sys_cabriolet.c` provides board support for Cabriolet-family Alpha systems, especially PC164 and LX164. It implements ISA-port interrupt masking and dispatch, SRM and PC164 interrupt workarounds, PCI slot IRQ mapping tables, Super I/O/IDE initialization, and machine vectors for LX164 and PC164.

## Important APIs, Types, And Functions
- `cached_irq_mask` mirrors disabled IRQ bits; here mask bit true means disabled.
- `cabriolet_update_irq_hw()`, `cabriolet_enable_irq()`, and `cabriolet_disable_irq()` write mask bytes to ISA ports 0x804-0x806.
- `cabriolet_irq_type` is the IRQ chip for platform IRQs.
- `cabriolet_device_interrupt()` reads summary ports 0x804-0x806 and dispatches bit 4 to ISA cascade or `handle_irq(16 + bit)`.
- `common_init_irq()` initializes i8259A, chooses SRM or native IRQ setup, installs level IRQ handlers, initializes ISA DMA, and requests ISA cascade.
- `cabriolet_init_irq()` and `pc164_init_irq()` specialize common init.
- `pc164_srm_device_interrupt()` and `pc164_device_interrupt()` raise `__min_ipl` during interrupt dispatch to work around broken PC164 interrupt masking.
- `eb66p_map_irq()`, `cabriolet_map_irq()`, and `alphapc164_map_irq()` are table-based PCI IRQ mappers.
- `cabriolet_enable_ide()` probes PC873xx Super I/O and enables IDE.
- `cia_cab_init_pci()` combines CIA PCI init and PC873xx IDE enable.
- `alphapc164_init_pci()` combines CIA PCI init and `SMC93x_Init()`.
- `lx164_mv` and `pc164_mv` define machine vectors.

## Control Flow
Native interrupt setup masks all summary ports, installs IRQ chips for Linux IRQs 16-34, and uses the i8259A for ISA cascade. Under SRM, it switches `alpha_mv.device_interrupt` to a supplied SRM dispatch function and initializes SRM IRQs. PC164 wraps both native and SRM dispatch with `__min_ipl = getipl()` to prevent recursive interrupts because hardware masking/ack is unreliable.

PCI IRQ mapping is purely table-driven by IDSEL and interrupt pin. LX164 uses Pyxis I/O and DAC offset, calls `pyxis_init_arch`, and initializes PCI with `alphapc164_init_pci()`. PC164 uses CIA I/O and the same AlphaPC164 IRQ map and SMC93x Super I/O initialization.

## State And Persistence
State includes `cached_irq_mask`, ISA summary/mask registers, IRQ descriptors, `__min_ipl` during PC164 dispatch, and Super I/O hardware configuration from SMC/PC873xx init. Machine vectors are init-time structures selected by setup.

## Dependencies And Integration Points
The file depends on CIA/Pyxis core logic, i8259A/ISA DMA helpers, SRM IRQ helpers, PC873xx Super I/O helpers, `SMC93x_Init()`, PCI common swizzle/table lookup, and machine-vector macros. `setup.c` selects `lx164_mv` or `pc164_mv` based on HWRPB variation.

## Risks
- Interrupt mask polarity differs from Alcor and is write-only through ISA ports, so software shadow state must stay correct.
- PC164 masking is known broken; the `__min_ipl` workaround reduces recursion but may affect interrupt latency.
- Several mapping tables are board-layout-specific; wrong vector selection misroutes PCI interrupts.
- `cia_cab_init_pci()` is present for Cabriolet-style IDE enable but not wired into the shown PC164/LX164 vectors, so callers must choose the right init path.
- Super I/O initialization can alter legacy device decode expected by firmware or other drivers.

## Test Signals
- PC164 and LX164 boot with correct machine vector and IRQ count 35.
- PCI devices receive expected interrupts on each slot/pin.
- PC164 handles interrupt load without recursive interrupt storms.
- SMC93x initialization finds and enables expected legacy devices.
- LX164 DMA can use `PYXIS_DAC_OFFSET` for DAC-capable devices.
