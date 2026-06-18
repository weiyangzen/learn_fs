<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.h

Purpose: Declares quicklist helpers for GM method address tracking.

Important APIs, types, and functions: Exposes `gm_addr_add`, `gm_addr_del`, and `gm_addr_search`, and aliases `bmi_gm_errno_to_pvfs` to the generic `bmi_errno_to_pvfs`.

Control flow and state: Header only. The functions mutate caller-owned quicklists of `struct gm_addr` entries.

Dependencies and integration points: Includes `quicklist.h` and `bmi-method-support.h`; paired with `bmi-gm-addressing.h` for `struct gm_addr` details. Included by `bmi-gm.c`.

Risks and test signals: The header does not document locking or ownership; GM code must serialize access around calls. Compile tests should catch mismatches with `bmi-gm-addressing.h`, and unit-style tests should validate search miss/hit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addr-list.h -->
