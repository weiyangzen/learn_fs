# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_format_caps.h

Purpose: declares Komeda format capability data structures, AFBC helper macros, and format capability APIs.

Important APIs/types/functions: AFBC macros wrap DRM AFBC modifier bits. Layer-type flags distinguish rich, simple, and writeback layers. Alignment constants define AFBC header/body/superblock requirements. `struct komeda_format_caps` records hardware format ID, fourcc, supported layer types, rotations, AFBC layouts, and AFBC features. `struct komeda_format_caps_table` stores the table and optional chip-specific predicate.

Control flow: D71 initializes a table; framebuffer and plane paths query it for caps and modifier support.

State and persistence: format tables are immutable chip data referenced by `komeda_dev->fmt_tbl`; `komeda_fb` stores a pointer to the selected caps.

Dependencies/integration: Linux types, DRM fourcc UAPI, D71 format table, framebuffer size/address handling, and plane format setup.

Risks: AFBC alignment constants feed memory-size validation; incorrect values can under-check buffers. Hardware IDs are consumed directly by D71 layer register programming. Test signals: framebuffer size validation, AFBC scanout, writeback format checks, and cross-checking hardware IDs against D71 docs.
