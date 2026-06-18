# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_uc_fw_abi.h

Purpose: Documents and defines packed ABI structures and bit fields for CSS-based, GSC-based, and late-binding firmware layouts used by Xe microcontroller firmware parsing.

Important APIs/types/functions: CSS definitions include `uc_css_rsa_info`, `uc_css_guc_info`, bit masks for time/version/build/header fields, and `uc_css_header` with a `static_assert` size of 128 bytes. GSC definitions include `gsc_version`, `gsc_partition`, `gsc_layout_pointers`, `gsc_bpdt_header`, `gsc_bpdt_entry`, `gsc_cpd_header_v2`, `gsc_cpd_entry`, and `gsc_manifest_header`. Late-binding definitions include `csc_fpt_header` and `csc_fpt_entry`.

Control flow: `xe_uc_fw.c` uses these structures to validate firmware blobs, locate manifests/CSS entries, extract versions/security version, and compute uCode/RSA offsets. The header itself has no executable control flow.

State and persistence behavior: Defines on-disk/in-blob layout interpretation only. Packed structs map directly onto firmware bytes; no kernel-owned state is stored here.

Dependencies and integration points: Includes build-bug and Linux types. It is part of the ABI contract between the kernel driver and GuC/HuC/GSC firmware image formats.

Risks: Packed layout, field widths, masks, and documented entry names must match firmware producer output exactly. Any structure change without firmware-format change coordination can break parsing. Parser code must continue to bounds-check before casting to these structs.

Test signals: Firmware parser tests using known-good and malformed CSS/GSC/late-binding blobs; static size/layout assertions; cross-check extracted versions against firmware release metadata.
