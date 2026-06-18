# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dccg/dcn32/dcn32_dccg.h

Purpose: this header declares the DCN 3.2 DCCG field map and create function. It reuses DCN 3.1 declarations while defining DCN 3.2-specific masks for DP stream clock source fields, OTG pixel-rate controls, DTBCLK_P controls, and dentist change-done/read/write divider fields.

Important APIs and types: `DCCG_MASK_SH_LIST_DCN32(mask_sh)` defines field mappings for DPP DTO enable/DB enable, DPP DTO phase/modulo, HDMI character/stream controls, PHY force controls, DP stream enable/source fields, `SYMCLK32` SE/LE controls, OTG DTO enable/status/source/add pixel fields, K1/K2 pixel-rate dividers, DTBCLK_P source/enables, audio DTO source, and dentist `CHG_DONE`, `RDIVIDER`, and `WDIVIDER`. The public symbol is `dccg32_create()`.

Control flow: resource construction expands this macro into `dccg_shift` and `dccg_mask` tables. Runtime behavior comes from `dcn32_dccg.c`, which relies on these fields being present for `REG_GET`, `REG_UPDATE`, `REG_WRITE`, and `REG_WAIT`.

State and persistence: the header has no mutable state. Its macro expansions become static metadata used by each `struct dcn_dccg` instance.

Dependencies and integration: it includes `dcn31/dcn31_dccg.h` and therefore inherits DCN 3.1 callback prototypes and common DCCG types. ASIC-specific resource files include this header to instantiate the register metadata for DCN 3.2 hardware.

Risks: the macro list includes a duplicate `OTG3_PIXEL_RATE_DIVK2` mapping. Missing DSCCLK fields here are deliberate because the DCN 3.2 C callback table does not expose local DSC DTO callbacks, but inherited callbacks still require compatible registers when used. Macro name concatenation is brittle against generated register-header changes.

Test signals: compile-time initialization of a DCN 3.2 DCCG table, successful `dccg32_create()` link, and runtime register writes for DP stream, DTBCLK_P, pixel divider, and dentist resync fields.
