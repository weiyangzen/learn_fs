# sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.h

Purpose: Declares machine-platform helper data and inline helpers for resolving SSP/TDM topology naming assumptions.

Important APIs/types: `struct avs_mach_pdata` carries codec pointer, TDM bitmap array, DMIC codec name, and obsolete-card naming flag. Inline helpers detect singular SSP, get SSP port, detect singular TDM slot, get TDM slot, and validate/fill both through `avs_mach_get_ssp_tdm()`. `AVS_STRING_FMT()` helps build SSP or SSP:TDM format strings.

Control flow role: Topology parsing and route/widget name substitution use these helpers to expand `%d` placeholders only when the machine describes exactly one SSP/TDM target.

State and persistence: No owned state; helpers read `snd_soc_acpi_mach` and pdata fields.

Dependencies and integration: Includes `<sound/soc-acpi.h>` and relies on kernel bit operations. Used by topology and PCM registration code. Exposes `obsolete_card_names` flag consumed by component registration.

Risks: Helpers assume `mach->pdata` is an `avs_mach_pdata` and that TDM arrays are valid for the selected port. `__ffs()` is only safe when masks are nonzero, so callers must respect singular checks.

Test signals: Machine entries with zero, one, and multiple SSP links; absent/present TDM arrays; dynamic topology names with and without `%d`; and obsolete-card-name registration behavior.
