# sources/distributed-fs/ceph-client/include/dt-bindings/bus/moxtet.h

Purpose: defines interrupt indexes for the Turris Mox Moxtet module configuration bus.

Important APIs/types/functions: constants assign PCI IRQ 0, USB3 IRQ 4, Peridot IRQs as `8 + n`, and Topaz IRQ 12.

Control flow: DTS interrupt specifiers use these indexes; the Moxtet bus/IRQ code maps them to module events.

State and persistence: IDs are stable DT ABI for Turris Mox modules.

Dependencies and integration: standalone DT binding used by Moxtet device trees and bus driver IRQ mapping.

Risks and test signals: wrong indexes misroute module interrupts. Test DTS validation and IRQ delivery for PCI, USB3, Peridot, and Topaz modules.
