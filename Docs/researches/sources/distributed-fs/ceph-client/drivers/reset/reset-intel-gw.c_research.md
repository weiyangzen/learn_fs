# sources/distributed-fs/ceph-client/drivers/reset/reset-intel-gw.c

Purpose: Intel Gateway/Lantiq-style RCU reset controller with reset-status polling and global restart support.

Important APIs/types/functions: `struct intel_reset_soc`, `struct intel_reset_data`, `id_to_reg_and_bit_offsets()`, `intel_set_clr_bits()`, assert/deassert/status ops, `intel_reset_xlate()`, `intel_reset_restart_handler()`, and `intel_reset_probe()`.

Control flow: OF match chooses legacy 3-cell or newer 2-cell format. Xlate packs reset register offset, request bit, and optional status bit into an ID. Operations update request bits through regmap and poll status offset. Probe maps MMIO regmap, reads `intel,global-reset`, registers the reset controller, computes reboot ID, and registers a restart handler.

State and persistence: register state is hardware-owned; packed IDs encode DT fields but are not persisted.

Dependencies and integration: postcore platform driver, OF properties, regmap MMIO, sys-off restart handler, reset framework.

Risks and test signals: legacy status register special case and packed ID bitfields must match bindings. Test both compatibles, global reset property length, timeout paths, restart assertion, and invalid bit >31 rejection.
