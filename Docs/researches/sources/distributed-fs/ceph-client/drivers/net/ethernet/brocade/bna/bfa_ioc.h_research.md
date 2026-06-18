# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_ioc.h

Purpose: public header for BNA IOC, mailbox, DMA, hardware-interface, notification, timeout, firmware-image, and flash service APIs.

Important APIs/types/functions: key constants include `BFA_IOC_TOV`, `BFA_IOC_HWSEM_TOV`, `BFA_IOC_HB_TOV`, `BFA_IOC_POLL_TOV`, `BNA_DBG_FWTRC_LEN`, `BFA_DMA_ALIGN_SZ`, SMEM sizes, and flash chunk helpers. Key types are `struct bfa_pcidev`, `struct bfa_dma`, `struct bfa_ioc_regs`, `struct bfa_mbox_cmd`, `struct bfa_ioc_mbox_mod`, callback typedefs and `struct bfa_ioc_cbfn`, `enum bfa_ioc_event`, `struct bfa_ioc_notify`, `struct bfa_iocpf`, `struct bfa_ioc`, `struct bfa_ioc_hwif`, `struct bfa_flash`, and `bfa_cb_flash`. Inline helpers set DMA addresses in BFI big-endian format via `bfa_dma_be_addr_set` and `bfa_alen_set`.

Control flow: consumers attach and initialize IOC state, provide PCI info, claim DMA memory, enable/disable IOC, register mailbox handlers/notifications, and service interrupts/timeouts by calling the declared functions. Hardware-specific code fills `struct bfa_ioc_hwif`; common code invokes those hooks for PLL init, register mapping, firmware locks, synchronization, failure notification, and firmware-state access. Flash callers attach, claim DMA memory, then issue asynchronous query/read/update operations with callbacks.

State and persistence behavior: `struct bfa_ioc` describes all runtime IOC state, including timers, hardware register mappings, firmware attributes, notification queues, mailbox handlers, ASIC/port configuration, and adapter capabilities. `struct bfa_flash` tracks an asynchronous flash operation, DMA bounce buffer, partition/offset/residue, callback, and IOC notification node. Persistent state is accessed through firmware/flash APIs but not stored by the header itself.

Dependencies and integration points: includes `bfa_cs.h` for FSM support, `bfi.h` for firmware message contracts, and `cna.h` for shared driver/kernel definitions. The declarations are used by `bfa_ioc.c`, hardware-specific IOC implementation files, CEE, flash users, BNA netdev code, and firmware image providers.

Risks: this header exposes internal state and hardware hooks widely, so module code can mutate fields without API guards. DMA address helpers intentionally encode addresses for firmware; using normal CPU endian values would break mailbox DMA. Timer constants define recovery behavior and can affect firmware boot reliability. The `bfa_ioc_hwif` contract must be completely populated for each ASIC generation or IOC operations will dereference null hooks.

Test signals: compile with CT and CT2 hardware backends, exercise IOC attach/pci-init/mem-claim/enable/disable, register a mailbox class and verify dispatch, and run flash/CEE clients through IOC failure notifications.
