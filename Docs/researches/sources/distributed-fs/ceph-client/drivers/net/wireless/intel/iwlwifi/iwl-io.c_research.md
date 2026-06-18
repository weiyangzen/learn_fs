# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.c

Purpose: Implements common iwlwifi MMIO and peripheral-register access wrappers, polling helpers, forced NMI triggering, FH/RFH debug dumps, NIC activation dispatch, and synchronous NMI/error notification flow.

Important APIs and functions: Exports `iwl_write8/32/64()`, `iwl_read32()`, `iwl_write_direct32/64()`, `iwl_read_prph()`, `iwl_write_prph_delay()`, `iwl_set_bits_prph()`, `iwl_set_bits_mask_prph()`, `iwl_clear_bits_prph()`, `iwl_force_nmi()`, `iwl_dump_fh()`, `iwl_trans_activate_nic()`, and `iwl_trans_sync_nmi_with_addr()`. Static `iwl_dump_rfh()` and register-name helpers format legacy FH or multi-queue RFH register state.

Control flow: Plain read/write wrappers trace accesses then call transport operations. Direct and PRPH helpers first grab NIC access, perform the operation, and release access; failures return sentinel timeout-looking values or silently skip writes. Poll helpers loop at 10 microsecond intervals until masked bits match or timeout. Forced NMI selects the correct register by device family. FH dump either allocates a debugfs buffer or logs register values. NMI sync disables interrupts if currently enabled, forces NMI, waits for firmware error indication, restores interrupts, and reports firmware error.

State and persistence: Mutates hardware registers, transport interrupt state, and firmware error/reset status. Allocated dump buffers are caller-owned. No durable storage exists.

Dependencies and integration points: Uses `iwl-trans` register methods, CSR/PRPH/FH register definitions, tracepoints, debug macros, PCIe gen1/2 NIC activation, debugfs conditionals, and transport firmware-error recovery.

Risks: NIC access must be held for direct/PRPH accesses. Family-specific NMI register selection is fragile. `iwl_set_bits_mask_prph()` writes `(old & mask) | bits`, so callers must pass masks matching intended preserved fields. Dump buffer sizing depends on register counts and RX queue count.

Test signals: Unit or hardware tests for poll timeout/success paths, PRPH access failures, family-specific NMI triggering, interrupt restore semantics, FH/RFH dump buffer generation, and debug traces for read/write offsets.
