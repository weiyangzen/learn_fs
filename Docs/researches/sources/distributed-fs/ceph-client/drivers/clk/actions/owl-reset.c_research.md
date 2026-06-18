# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.c

Purpose: this file implements reset-controller operations for Actions OWL CMU reset bits.

Important functions: `owl_reset_assert()` clears the mapped bit with `regmap_update_bits()`. `owl_reset_deassert()` sets the mapped bit. `owl_reset_reset()` asserts, waits 1 microsecond, then deasserts. `owl_reset_status()` reads the register and returns the logical reset API status, explicitly inverting the hardware convention because set means not asserted.

Control flow/state: reset state is stored in CMU reset registers. The controller uses an ID-indexed `owl_reset_map` supplied by the SoC descriptor.

Dependencies and integration: SoC probes allocate `struct owl_reset`, point it at the shared regmap and static reset map, then register `owl_reset_ops` through `devm_reset_controller_register()`.

Risks and tests: there is no bounds check in the callbacks; the reset core must pass valid IDs less than `nr_resets`. Sparse reset arrays can leave zero-initialized map entries if IDs are missing. Test signals are reset assert/deassert/status for each DT reset ID and verifying hardware active-low semantics.
