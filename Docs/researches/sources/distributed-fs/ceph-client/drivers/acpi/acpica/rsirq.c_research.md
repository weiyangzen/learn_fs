# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsirq.c

Purpose: defines conversion tables for IRQ, extended IRQ, DMA, and fixed DMA resource descriptors.

Important APIs, types, and functions: table symbols are `acpi_rs_get_irq`, `acpi_rs_set_irq`, `acpi_rs_convert_ext_irq`, `acpi_rs_convert_dma`, and `acpi_rs_convert_fixed_dma`.

Control flow: short IRQ get decodes a 16-bit IRQ mask to an interrupt list, sets default edge-sensitive triggering, reads whether the optional flags byte exists, and exits early when absent. IRQ set encodes the list back to a bitmask, writes flags, and can optimize from a 3-byte descriptor to a 2-byte no-flags descriptor when triggering, polarity, and sharing match ACPI defaults. Extended IRQ moves producer/consumer, triggering, polarity, sharing, wake, interrupt count, a variable dword interrupt array, and optional resource source. DMA converts transfer/bus-master/type flags and an 8-bit channel mask. Fixed DMA moves request lines, channels, and width.

State and persistence: static conversion tables only.

Dependencies and integration points: relies on bitmask helpers in `rsutils.c`, the generic conversion interpreter in `rsmisc.c`, size logic in `rscalc.c`, and dispatch from `rsinfo.c`.

Risks and test signals: malformed interrupt counts and bitmasks are sensitive because they affect variable internal length. IRQ no-flags optimization has the same compatibility caveat as start-dependent functions. Extended IRQ must enforce at least one interrupt through validation elsewhere. Tests should cover empty/full IRQ masks, multiple extended interrupts, optional resource source, wake/share flags, DMA masks, fixed DMA widths, and conversion of default flags to compact AML descriptors.
