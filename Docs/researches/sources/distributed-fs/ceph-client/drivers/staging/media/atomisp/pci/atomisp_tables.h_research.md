# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_tables.h

Purpose: provides static ISP color/effect tuning tables used by atomisp image effects. It contains color correction matrices for sepia, negative, and mono, MACC tables for skin, blue, and green effects, and a CTC table for vivid rendering.

Important APIs/types/functions: the file exports header-local `static` data objects: `sepia_cc_config`, `nega_cc_config`, `mono_cc_config`, `skin_low_macc_table`, `skin_medium_macc_table`, `skin_high_macc_table`, `blue_macc_table`, `green_macc_table`, and `vivid_ctc_table`. These use CSS types from `sh_css_params.h`.

Control flow: there is no runtime control flow. Inclusion gives a translation unit private copy of the tables and callers select/copy them into CSS parameter structures when enabling user-visible effects.

State and persistence: the tables are compile-time constants in practice, though not declared `const`. They do not persist user state and do not mutate hardware directly.

Dependencies and integration: integrated with CSS color correction, MACC, and CTC configuration paths. The values must match CSS firmware expectations for table shape and fixed-point interpretation.

Risks and test signals: because the objects are `static` in a header and not `const`, each includer can get mutable private storage and accidental writes are possible. Build tests should catch CSS type layout changes; image-effect tests should verify visual output and parameter upload for each effect.
