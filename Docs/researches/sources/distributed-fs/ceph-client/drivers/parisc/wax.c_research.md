# sources/distributed-fs/ceph-client/drivers/parisc/wax.c

## Purpose
`wax.c` is the PA-RISC WAX bus-adapter driver. It discovers the WAX GSC ASIC, disables and initializes its interrupt block, claims the fixed GSC interrupt line, registers common GSC resources, and assigns child-device interrupt lines for WAX-attached i8042, serial, and EISA functions.

## Important APIs, Types, and Functions
The file is built around the PA-RISC driver model: `struct parisc_driver wax_driver`, `struct parisc_device_id wax_tbl`, and `arch_initcall(wax_init)`. `wax_init_chip()` allocates and fills `struct gsc_asic`, claims IRQ routing with `gsc_claim_irq()`, installs `gsc_asic_intr` with `request_irq()`, calls `gsc_common_setup()`, and finally performs interrupt fixups. `wax_choose_irq()` maps known `dev->id.sversion` values to primary and optional auxiliary ASIC IRQ inputs through `gsc_asic_assign_irq()`. `wax_init_irq()` masks the ASIC, clears pending interrupt state, and leaves firmware-managed resets commented out.

## Control Flow
At architecture init, `register_parisc_driver()` binds WAX devices matching HPHW_BA sversion `0x0008e`. Probe allocates a zeroed ASIC structure, records `dev->hpa.start`, masks/clears interrupts, claims hardcoded `WAX_GSC_IRQ` 7, derives the EIM value from the claimed transaction address/data, requests the actual CPU IRQ, writes the EIM to the WAX IAR, and enters common GSC setup. IRQ fixup runs over WAX children and, on 715-class layouts where WAX EISA is a sibling rather than child, over the parent as well.

## State and Persistence
Runtime state is in the allocated `struct gsc_asic`: name, HPA, version, GSC IRQ metadata, and EIM. Hardware state is the interrupt mask/request/address registers under the WAX HPA. There is no persistent storage and no module exit path because this is early platform init.

## Dependencies and Integration Points
The driver depends on PA-RISC platform headers, `gsc.h`, the PARISC bus, and GSC interrupt helpers. It integrates with child drivers by filling `dev->irq` and `dev->aux_irq`, not by directly driving child hardware.

## Risks
The fixed IRQ mapping is sversion-specific; unknown devices silently keep existing IRQ state. Failure after `request_irq()` but before or inside `gsc_common_setup()` frees the ASIC object but does not explicitly free the requested IRQ in the error branch, so cleanup correctness depends on setup failure expectations. The parent dereference assumes `parisc_parent(dev)` is non-null.

## Test Signals
Boot on WAX-equipped PA-RISC hardware should log `wax at 0x... found`, successfully route interrupts for i8042/serial/EISA, and avoid spurious WAX interrupts after masking and IRR clearing. Regression signals are missing keyboard/serial/EISA IRQs or `cannot get GSC irq`.
