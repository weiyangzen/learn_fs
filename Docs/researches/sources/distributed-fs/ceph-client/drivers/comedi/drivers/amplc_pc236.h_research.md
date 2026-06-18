# sources/distributed-fs/ceph-client/drivers/comedi/drivers/amplc_pc236.h Research

Defines shared board/private structures and the common attach prototype for Amplicon PC236-family drivers.

`struct pc236_board` contains the board name and optional callbacks for updating interrupt hardware and checking/clearing interrupt status. `struct pc236_private` stores a PLX local configuration I/O base for PCI variants and an `enable_irq` software flag. The header declares `amplc_pc236_common_attach()`.

No executable flow exists in the header. The callback pointers allow ISA and PCI front-ends to share the common interrupt command implementation while providing hardware-specific enable/check behavior. `enable_irq` persists command active state between start/cancel and ISR checks.

Dependencies are Linux types and a forward declaration of `struct comedi_device`. It is included by front-end and common Amplicon PC236 files. Risks include callback contract ambiguity and private fields used only by some variants. Tests are compile/link coverage plus runtime checks that callbacks are optional for ISA, present for PCI variants, and that `enable_irq` is consistently updated under the common spinlock.
