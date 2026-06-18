# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/nark.c

Purpose: provides the minimal hardware interface for NEMER/ARK split-BAR AAC controllers. It adapts the RX miniport to controllers whose register and memory windows are exposed through different PCI BAR layout semantics.

Important APIs/types/functions: `aac_nark_ioremap()` maps and unmaps the split register windows and sets `dev->IndexRegs`; `aac_nark_init()` installs the ioremap and communication-selection operations before delegating to `_aac_rx_init()`. It uses `struct rx_registers`, `struct aac_dev`, PCI resource accessors, `ioremap()`, `iounmap()`, and RX common routines.

Control flow: `aac_nark_init()` sets `dev->a_ops.adapter_ioremap = aac_nark_ioremap` and `adapter_comm = aac_rx_select_comm`, then calls `_aac_rx_init()`. On map requests, the driver builds the RX register address from BAR0 and BAR1 values, maps enough for the RX registers excluding the inbound region, sets `base_start` from BAR2, maps the main base window, and points `IndexRegs` at the mapped base. On unmap requests, it releases both mappings and clears pointers.

State and persistence: it owns no protocol state beyond `dev->regs.rx`, `dev->base`, `dev->base_start`, and `dev->IndexRegs`. All queue, FIB, interrupt, and firmware state is initialized by the shared RX path.

Dependencies and integration: depends on RX miniport behavior from `rx.c`, common PCI BAR resources, and the `dev->a_ops` initialization contract used by `linit.c`.

Risks and test signals: the split address computation combines BAR0 and BAR1 into a 64-bit register address, so incorrect PCI resources or platform quirks can map the wrong region. Test BAR mapping success/failure, unmap after partial map failure, `IndexRegs` offset correctness, producer and message communication selection through RX, and probe/remove reset flows for NEMER/ARK IDs.
