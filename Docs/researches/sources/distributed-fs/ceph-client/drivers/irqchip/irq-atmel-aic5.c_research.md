# sources/distributed-fs/ceph-client/drivers/irqchip/irq-atmel-aic5.c

## Purpose
Implements newer Atmel/Microchip AIC5 controllers, which can expose up to 128 interrupt lines through a selected-source register interface.

## Important APIs, Types, and Functions
Registered init wrappers cover SAMA5D2, SAMA5D3, SAMA5D4, SAM9X60, and SAM9X7 compatibles. Core logic is in `aic5_of_init()`, `aic5_handle()`, `aic5_mask()`, `aic5_unmask()`, `aic5_retrigger()`, `aic5_set_type()`, PM callbacks, and `aic5_irq_domain_xlate()`.

## Control Flow
Variant init chooses the IRQ count and optionally allocates `smr_cache`. Common init builds the domain/generic chips. The driver fills chip callbacks for each 32-line chunk, initializes every source by selecting it in SSR, programming SVR, disabling, and clearing, then installs the root handler. Dispatch reads IVR/ISR and handles or EOIs like classic AIC.

## State and Persistence
`aic5_domain` is global. AIC5 shared registers require locking on the first generic chip while selecting SSR. PM may persist SMR values in `smr_cache`, and generic-chip `mask_cache`/`wake_active` drive suspend/resume masking.

## Dependencies and Integration Points
Uses common AIC helpers, generic irqchip, OF irqchip declarations, and ARM root IRQ handling. Integrates with SoC fixups for RTC/RTT and with DT three-cell interrupt specs.

## Risks and Test Signals
Risks include SSR races, incorrect per-SoC IRQ counts, missing SMR restore on SAMA5D2, and mask-cache divergence because all chips share one register selector. Test signals include successful boot on each compatible, trigger/priority programming per DT, working wake behavior, and no invalid hwirq access past `revmap_size`.
