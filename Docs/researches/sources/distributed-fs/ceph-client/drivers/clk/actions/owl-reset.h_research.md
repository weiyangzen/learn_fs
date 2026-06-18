# sources/distributed-fs/ceph-client/drivers/clk/actions/owl-reset.h

Purpose: this header declares the OWL reset controller data model.

Important types: `struct owl_reset_map` maps a reset ID to a register and bit mask. `struct owl_reset` embeds `reset_controller_dev`, the reset map pointer, and the regmap. `to_owl_reset()` converts reset core callbacks back to this structure. `owl_reset_ops` is exported from `owl-reset.c`.

Control flow/state: the header itself has no logic. Runtime reset state remains in hardware, while `owl_reset` stores the static map and shared regmap needed by callbacks.

Dependencies and integration: included by SoC clock descriptor files and by `owl-common.h` through forward-declared descriptor references. DT binding reset IDs index the SoC reset map arrays.

Risks and tests: map array size and DT binding IDs must remain aligned. Since the map stores a full bit mask rather than a bit index, callers must pass `BIT(n)` values. Test signals are reset-controller registration, reset ID coverage, and invalid-ID protection at the reset core boundary.
