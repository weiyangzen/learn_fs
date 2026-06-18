# sources/distributed-fs/ceph-client/sound/soc/sof/intel/ext_manifest.h

Purpose: `ext_manifest.h` defines Intel cAVS-specific extended manifest platform configuration structures. These metadata entries live outside the signed firmware image and let the HDA code consume platform-specific firmware hints such as clock policy and mailbox sizes.

Important types: `enum sof_cavs_config_elem_type` defines tokens for empty entries, LPRO clock configuration, outbox size, and inbox size. `struct sof_ext_man_cavs_config_data` wraps a generic `struct sof_ext_man_elem_header` followed by a flexible array of `struct sof_config_elem` values and is marked packed to match firmware binary layout.

Control flow and integration: the header is consumed by `hda-loader.c`, specifically `hda_dsp_ext_man_get_cavs_config_data()`. That parser uses `container_of()` from a generic extended manifest element header, computes the element count from the header size, and handles these tokens.

State and persistence behavior: parsed values are firmware-provided persistent runtime configuration. Currently the LPRO token updates `struct sof_intel_hda_dev::clk_config_lpro`; inbox/outbox size tokens are recognized but ignored. Unsupported token types are logged.

Dependencies and risks: this header depends on `<sound/sof/ext_manifest.h>` for common manifest element definitions. Risks are binary compatibility and bounds: the flexible-array layout must match firmware exactly, and parser changes must validate `hdr->size` before walking elements. Test signals include loading firmware with cAVS platform config, confirming LPRO/HPRO debug logs, rejecting inconsistent element counts, and ensuring unknown tokens do not abort boot unless policy changes.
