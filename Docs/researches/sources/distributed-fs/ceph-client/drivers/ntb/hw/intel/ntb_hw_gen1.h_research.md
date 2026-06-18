# sources/distributed-fs/ceph-client/drivers/ntb/hw/intel/ntb_hw_gen1.h

Purpose: Defines Gen1/Xeon Intel NTB register offsets, topology/PPD masks, resource counts, B2B address defaults, hardware errata flags, and prototypes exported from `ntb_hw_gen1.c` for reuse by gen3/gen4.

Important APIs, types, and functions: Constants cover PBAR/SBAR limits, translations, sizes, base registers, PPD, doorbells, scratchpads, link status, B2B registers, and hardware error flags. `XEON_MW_COUNT`, `HSX_SPLIT_BAR_MW_COUNT`, `XEON_DB_COUNT`, and `XEON_SPAD_COUNT` define Gen1 resource exposure. Externs `xeon_b2b_usd_addr` and `xeon_b2b_dsd_addr` provide configurable B2B translation defaults. Prototypes expose common helpers such as `ndev_init_isr()`, `xeon_ppd_topo()`, DB/SPAD helpers, MW/link callbacks, and `xeon_link_is_up()`.

Control flow: No direct runtime flow, but the constants and prototypes parameterize Gen1 init and are intentionally shared by gen3/gen4 for common NTB operations and B2B address policy.

State and persistence behavior: The header defines persistent hardware locations rather than allocating state. Errata flags are stored at runtime in `intel_ntb_dev.hwerr_flags` and interpreted by common helpers.

Dependencies and integration points: Includes `ntb_hw_intel.h`. It connects the gen1 implementation to gen3/gen4 implementations, which reuse Gen1 helper callbacks and B2B address defaults.

Risks and edge cases: The header is a shared contract beyond Gen1, so changing helper signatures or B2B constants can break gen3/gen4. BAR offset macros encode split and unsplit BAR interpretations at overlapping offsets; caller logic must select the correct one based on `bar4_split`.

Test signals: Compile coverage across gen1/gen3/gen4, Gen1 topology tests for all PPD encodings, split/non-split BAR debugfs verification, and errata-specific behavior tests are the main validation signals.
