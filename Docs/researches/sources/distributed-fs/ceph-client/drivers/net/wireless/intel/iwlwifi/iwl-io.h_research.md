# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/iwl-io.h

Purpose: Declares the common IO helper API for MMIO, direct NIC, PRPH, UMAC PRPH, polling, NMI, NIC activation, and FH dump operations.

Important APIs and types: Prototypes cover `iwl_write8/32/64()`, `iwl_read32()`, direct reads/writes, PRPH no-grab and grab variants, bit setters/clearers, `iwl_force_nmi()`, `iwl_trans_activate_nic()`, and `iwl_dump_fh()`. Inline helpers include `iwl_set_bit()`, `iwl_clear_bit()`, `iwl_poll_bits()`, `iwl_write_prph()`, and UMAC PRPH offset wrappers.

Control flow: Inline helpers route simple bit updates through transport `set_bits_mask`, convert generic UMAC offsets by adding `trans->mac_cfg->umac_prph_offset`, and delegate polling to C implementations.

State and persistence: Header owns no state but exposes calls that mutate device registers and transport error/reset status. UMAC helper correctness depends on immutable per-device offset configuration.

Dependencies and integration points: Includes `iwl-devtrace.h` and `iwl-trans.h`; consumed widely by transport, scheduler, firmware-load, debug, and device-family code.

Risks: No-grab PRPH helpers require callers to already hold NIC access. UMAC offset wrappers must be used only for peripheries that moved between families. Incorrect bit-mask calls can clear or preserve unexpected register fields.

Test signals: Build coverage across device families, sparse/lockdep checks around NIC access, and hardware tests for UMAC PRPH reads/writes on pre-AX200 and AX200+ devices.
