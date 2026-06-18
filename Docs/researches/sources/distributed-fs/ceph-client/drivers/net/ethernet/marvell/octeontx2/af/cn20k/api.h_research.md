# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/api.h

Purpose: Declares the CN20K-specific extension API for RVU Admin Function mailbox setup, mailbox memory management, and AF/PF/VF interrupt control.

Important APIs/types/functions: `struct ng_rvu` holds CN20K next-generation RVU extension state: `rvu_mbox_ops`, PF mailbox `qmem`, and VF mailbox `qmem`. Function prototypes include `cn20k_rvu_mbox_init()`, `cn20k_rvu_get_mbox_regions()`, `cn20k_free_mbox_memory()`, `cn20k_register_afpf_mbox_intr()`, `cn20k_register_afvf_mbox_intr()`, `cn20k_rvu_enable_mbox_intr()`, `cn20k_rvu_unregister_interrupts()`, `cn20k_mbox_setup()`, `cn20k_rvu_enable_afvf_intr()`, and `cn20k_rvu_disable_afvf_intr()`.

Control flow and integration: Core RVU AF code calls these declarations when running on CN20K hardware. The implementation in `mbox_init.c` allocates shared mailbox memory, installs mailbox operation handlers, registers interrupts, and enables/disables interrupt masks.

State and persistence: `struct ng_rvu` persists as part of `struct rvu` during AF lifetime. Its qmem pointers own DMA/IOVA-backed mailbox regions until freed.

Dependencies: Includes `../rvu.h` and relies on `struct rvu`, `struct qmem`, `struct mbox_ops`, `struct otx2_mbox`, and PCI device types.

Risks: The header is a cross-module contract; mismatched definitions between core RVU and CN20K implementation cause build or runtime mailbox failures. Memory ownership is implicit: callers must ensure `cn20k_free_mbox_memory()` runs after successful allocation.

Test signals: CN20K AF probe, mailbox init for AFPF and AFVF, interrupt registration, PF/VF message exchange, and teardown memory cleanup validate the API.
