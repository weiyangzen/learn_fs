<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x-udc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x-udc.h

Purpose: PXA27x USB device controller register and bit definitions.

Important definitions: UDC control/status registers (`UDCCR`, `UDCICR*`, `UDCISR*`, `UDCFNR`, `UDCOTGICR`, `UP2OCR`, `UP3OCR`), endpoint status registers `UDCCSR*`, byte-count registers `UDCBCR*`, data registers `UDCDR*`, endpoint configuration registers `UDCCR*`, and bit masks for OTG, interrupts, FIFO, endpoint type/direction, packet status, and byte-count limits.

Control flow and integration: no executable code; UDC driver code includes these macros to perform direct MMIO register operations.

State and persistence: hardware register values persist in the UDC until reset or driver reconfiguration.

Dependencies: includes `pxa-regs.h` and forbids simultaneous inclusion with PXA25x UDC support.

Risks and test signals: direct `__REG` access requires the PXA IO mapping. Incorrect bit masks cause USB enumeration or endpoint failures. Test USB gadget enumeration, endpoint interrupts, FIFO handling, OTG events, and build guard conflict with PXA25x UDC headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa27x-udc.h -->
