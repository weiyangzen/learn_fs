# sources/distributed-fs/ceph-client/drivers/media/platform/raspberrypi/rp1-cfe/cfe.h

Purpose: shared RP1 CFE definitions for format lookup and remapping across the core, CSI-2, and FE components.

Important APIs/types/functions: declares `enum cfe_remap_types`, format flags, `struct cfe_fmt`, `cfe_default_format`, `find_format_by_code()`, `find_format_by_pix()`, `cfe_find_16bit_code()`, and `cfe_find_compressed_code()`.

Control flow: no direct runtime flow; consumers call lookup/remap helpers implemented in `cfe.c`.

State and persistence: no mutable state. `cfe_fmt` instances are static table entries in `cfe-fmts.h`.

Dependencies and integration: includes media bus and V4L2 types. Used by `cfe.c`, `csi2.c`, and `pisp-fe.c` to keep format semantics consistent.

Risks: flags and remap enum order are ABI-internal but cross-file; changing them requires synchronized updates to the static format table and users.

Test signals: build/link coverage for helper declarations and behavioral tests where CSI-2/FE remap decisions match the format table.
