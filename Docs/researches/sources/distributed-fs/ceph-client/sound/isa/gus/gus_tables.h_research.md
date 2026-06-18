<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_tables.h -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gus_tables.h

Purpose: shared declarations and optional allocation for GF1 lookup tables.

Important APIs/types/functions: defines table sizes `SNDRV_GF1_SCALE_TABLE_SIZE` and `SNDRV_GF1_ATTEN_TABLE_SIZE`. When `__GUS_TABLES_ALLOC__` is defined, it allocates `snd_gf1_atten_table`; otherwise it declares externs. A disabled scale table remains under `#if 0`.

Control flow: `gus_volume.c` defines `__GUS_TABLES_ALLOC__` before including this header, creating the attenuation table and exporting it. Other users include it for extern declarations.

State and persistence: the attenuation table is static read-only data used by synth-related code; no runtime mutation.

Dependencies and integration: exported for `snd-gus-synth` module via `EXPORT_SYMBOL(snd_gf1_atten_table)` in `gus_volume.c`. Risks are ABI/data compatibility with external synth code and accidental multiple definitions if allocation macro is misused. Test signals are successful link with one definition, synth module resolving the symbol, and table bounds matching 128 entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gus_tables.h -->
