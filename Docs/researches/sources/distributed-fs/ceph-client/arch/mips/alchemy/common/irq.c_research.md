# sources/distributed-fs/ceph-client/arch/mips/alchemy/common/irq.c

## Purpose
`irq.c` initializes and manages Alchemy interrupt controllers. It supports the classic dual 32-source interrupt controllers used by Au1000 through Au1200 and the Au1300 GPIC, including IRQ type programming, masking/unmasking, wake controls, priority assignment, chained dispatch from MIPS CPU IRQ lines, GPIC pin-function helpers, and syscore suspend/resume state save.

## Important APIs, Types, And Functions
`struct alchemy_irqmap` maps Linux IRQ numbers to trigger type, priority, and Au1300 internal-source metadata. CPU-specific maps cover Au1000, Au1500, Au1100, Au1550, Au1200, and Au1300. Main architecture entry points are `arch_init_irq()` and `plat_irq_dispatch()`. Classic interrupt chip callbacks include `au1x_ic0_unmask()`, `au1x_ic1_unmask()`, `au1x_ic0_mask()`, `au1x_ic1_mask()`, `au1x_ic0_ack()`, `au1x_ic1_ack()`, `au1x_ic0_maskack()`, `au1x_ic1_maskack()`, `au1x_ic1_setwake()`, and `au1x_ic_settype()`.

Au1300 exported helpers include `au1300_pinfunc_to_gpio()`, `au1300_pinfunc_to_dev()`, `au1300_set_irq_priority()`, and `au1300_set_dbdma_gpio()`. GPIC callbacks include `au1300_gpic_mask()`, `au1300_gpic_unmask()`, `au1300_gpic_maskack()`, `au1300_gpic_ack()`, and `au1300_gpic_settype()`. Init helpers are `au1000_init_irq()` and `alchemy_gpic_init_irq()`.

## Control Flow
`arch_init_irq()` selects classic or GPIC initialization based on CPU type. Classic initialization resets both controllers to a safe state, registers syscore PM, initializes MIPS CPU IRQs, sets all 64 possible sources to `IRQ_TYPE_NONE`, applies the CPU-specific map with trigger type and priority assignment, then chains CPU IRQ lines 2-5 to request dispatchers. Each dispatcher reads a request register and forwards the first pending source to `generic_handle_irq()`.

Au1300 initialization disables and acknowledges all four GPIC banks, registers the GPIC syscore PM, initializes all GPIC IRQs to disabled/type none and priority 1, applies known on-chip source types/priorities, switches internal multifunction pins to device function, and chains CPU IRQ lines 2-5 to a priority encoder dispatcher. Runtime `irq_set_type()` calls update hardware trigger bits and handler names. `plat_irq_dispatch()` maps the first pending CPU interrupt bit to `do_IRQ()`.

## State And Persistence
Persistent state includes interrupt-controller configuration registers, masks, wake bits, source assignment, trigger type, priority, GPIC pin configuration, GPIC DMA trigger selection, and chained handler registrations. Syscore suspend snapshots classic IC config/source/assignment/wake/mask state or GPIC masks/DMASEL/pin configs, disables interrupts, and restores state on resume.

## Dependencies And Integration Points
It depends on the MIPS CPU interrupt controller, generic IRQ core, syscore PM, Alchemy register mappings, GPIO Au1300 pin helpers, and CPU type detection. Board files call `irq_set_irq_type()` for board GPIO lines after this file has registered chips. `gpiolib.c` maps GPIO lines to IRQs provided here. `power.c` and `sleeper.S` rely on wake-capable interrupt state around sleep.

## Risks
Dispatcher functions handle only the first set pending bit per chained interrupt; fairness and retriggering depend on controller behavior. `plat_irq_dispatch()` uses `__ffs(r & 0xff)` without an explicit zero check, assuming it is called only with a pending CPU interrupt. Trigger programming changes irq chip/handler while holding IRQ core locks and must stay consistent with hardware bits. Classic `irq_set_wake` only supports IC1 bits 0-7, so callers can receive `-EINVAL`. GPIC pinmux helpers can steal pins from devices or GPIO depending on use. Suspend/resume state arrays are shared for classic and GPIC modes and sized for both; indexing mistakes would be severe.

## Test Signals
Boot every supported Alchemy CPU type and verify `arch_init_irq()` selects the expected map. Use `/proc/interrupts` and IRQ debug data to confirm chip names, trigger handlers, and priorities. Exercise UART, timer, RTC, DMA, USB, MAC, PCI, GPIO edge/level, and Au1300 internal interrupts. Test `irq_set_irq_type()` transitions, wake enable/disable for supported GPIO lines, suspend/resume interrupt restoration, and GPIC multifunction pin switching. Inject spurious chained requests where possible to verify spurious handling.
