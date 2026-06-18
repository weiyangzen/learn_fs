# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_link.h

- Purpose: Shared CAM/PCMCIA/HIF data model and prototypes for the Mantis conditional-access path.
- Important APIs/types/functions: `enum mantis_sbuf_status`, `struct mantis_slot`, `enum mantis_slot_state`, `struct mantis_ca`, CAM event, PCMCIA, EVM, and HIF function prototypes.
- Control flow: CA code allocates/fills `struct mantis_ca`; IRQ/work handlers update slot state and wait queues; HIF functions provide EN50221 memory/I/O access.
- State and persistence: State includes four slot descriptors, wait queues, smart-buffer status/event bits, slot state, CA private pointer, EN50221 object, and mutex. No persistence.
- Dependencies and integration points: Ties DVB CA EN50221 integration to `mantis_evm.c`, `mantis_pcmcia.c`, `mantis_hif.c`, and the larger Mantis PCI object.
- Risks: The implementation only treats slot 0 as active although arrays are sized for four. Wait-queue and status fields are shared with IRQ/work contexts.
- Test signals: CAM insertion/removal, EN50221 application access, HIF timeout, and module unload tests.
