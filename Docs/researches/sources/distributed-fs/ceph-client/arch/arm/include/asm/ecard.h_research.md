# sources/distributed-fs/ceph-client/arch/arm/include/asm/ecard.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/ecard.h` declares expansion-card data
structures and driver registration APIs for Acorn-style ARM ecard buses. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `MANU_ACORN`, `PROD_ACORN_SCSI`, `PROD_ACORN_ETHER1`, `PROD_ACORN_MFM`, `MANU_ANT2`,
`PROD_ANT_ETHER3`, `MANU_ATOMWIDE`, `PROD_ATOMWIDE_3PSERIAL`, `MANU_IRLAM_INSTRUMENTS`,
`MANU_IRLAM_INSTRUMENTS_ETHERN`, `MANU_OAK`, `PROD_OAK_SCSI`, `MANU_MORLEY`,
`PROD_MORLEY_SCSI_UNCACHED`, `MANU_CUMANA`, `PROD_CUMANA_SCSI_2`, `PROD_CUMANA_SCSI_1`, `MANU_ICS`,
and 40 more; types: `ecard_id`, `in_ecid`, `expansion_card`, `device`, `resource`, `in_chunk_dir`,
`ecard_driver`, `device_driver`, `ecard_t`, `loader_t`, `expansion_card_ops`; functions/prototypes:
`ecard_setirq`, `ecard_readchunk`, `ecard_request_resources`, `ecard_release_resources`,
`ecard_register_driver`, `ecard_remove_driver`, `ecard_bus_type`. The file is 219 lines / 6125
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
Caller-visible state is represented by `ecard_id`, `in_ecid`, `expansion_card`, `device`,
`resource`, `in_chunk_dir`, `ecard_driver`, `device_driver`, and 3 more. External state or
implementation hooks include `ecard_readchunk`, `ecard_request_resources`,
`ecard_release_resources`, `ecard_bus_type`. DMA-visible state depends on cache cleanliness, bus
mappings, and device/platform data owned by the DMA mapping or driver layers. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. It integrates with generic Linux ARM architecture
code through include-time contracts rather than a standalone translation unit. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ecard.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
