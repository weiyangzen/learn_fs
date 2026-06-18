# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_ddi_buf_trans.h

Purpose: defines the common DDI buffer translation data model shared between the static translation tables in `intel_ddi_buf_trans.c` and the DDI/PHY programming paths in `intel_ddi.c`. It abstracts several generations of Intel display PHY tuning entries behind one union and exposes initialization and HOBL identification helpers.

Important APIs/types/functions: entry structs describe the register payloads for each hardware family: `hsw_ddi_buf_trans` (`trans1`, `trans2`, `i_boost`), `bxt_ddi_buf_trans` (`margin`, `scale`, `enable`, `deemphasis`), `icl_ddi_buf_trans` (`dw2_swing_sel`, `dw7_n_scalar`, cursor/post-cursor coefficients), `icl_mg_phy_ddi_buf_trans`, `tgl_dkl_phy_ddi_buf_trans`, `dg2_snps_phy_buf_trans`, and `xe3plpd_lt_phy_buf_trans`. `union intel_ddi_buf_trans_entry` overlays these layouts. `struct intel_ddi_buf_trans` points to an entry array and stores `num_entries` plus the `hdmi_default_entry`. Public functions are `is_hobl_buf_trans()` and `intel_ddi_buf_trans_init()`.

Control flow: no executable control flow is defined here. The intended flow is that `intel_ddi_buf_trans_init()` assigns an encoder table selector; later DDI code fetches a `struct intel_ddi_buf_trans`, chooses an entry index from HDMI defaults or DP training state, and interprets the entry through the union member matching the active PHY programming callback.

State and persistence: this header owns no state. The structures represent immutable static tables in the C file and transient pointers returned through `encoder->get_buf_trans`. The only stateful aspect is semantic: the caller must know which union member is valid for the selected platform.

Dependencies and integration: includes Linux integer types and forward declares `intel_encoder` and `intel_crtc_state`. It is included by DDI core code and by platform PHY code that needs table entries. The data shapes mirror hardware register fields documented by BSpec and consumed by HSW/SKL DDI, BXT DPIO, ICL combo/MG, TGL DKL, DG2/MTL SNPS, and XE3 LPD LT PHY implementations.

Risks: the union gives compile-time convenience but little type safety; a selector bug can make a caller read `.icl` fields from an `.snps` table. `num_entries` is an 8-bit count, so callers must still clamp indices. HDMI defaults are table-local and must be set for HDMI-capable tables. Adding a new PHY requires extending both this header and all selector/programming consumers consistently.

Test signals: compile all DDI PHY families, run modesets that exercise each union member, and verify link training and HDMI default selection on representative hardware. Static review should confirm every table's `num_entries` matches its array and every selected table matches the active `set_signal_levels` implementation.
