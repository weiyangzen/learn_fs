<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru-regs.h -->
## sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru-regs.h

Purpose: centralizes symbolic register IDs and bit definitions for CRU common logic across RZ/G2L and RZ/G3E-style variants.

Important APIs/types/functions: defines bit helpers for CRU control/status, memory bank addresses, AXI attributes, FIFO pointers, image stride, image conversion enable/control, CSI virtual channel selection, and output data mode. `enum rzg2l_cru_common_regs` is the key ABI between code and variant-specific offset tables in `rzg2l-core.c`; each enum value indexes `cru->info->regs`.

Control flow and state: no executable control flow. Runtime read/write helpers in `rzg2l-video.c` consume these IDs and map them through variant offset arrays.

Dependencies and integration points: requires kernel bit macros such as `BIT()` and `GENMASK()` from including C files. It is included by CRU core, IP, and video files. `AMnMBxADDRL/H(x)` depend on enum ordering where bank address IDs are sequential pairs.

Risks: enum ordering is a hard contract; inserting values without updating every variant offset array can make register writes target wrong hardware addresses. Some IDs are unavailable on a given variant and are represented by zero offsets, so call sites must only use registers valid for that variant or rely on guarded helpers. `AMnMBxADDRL/H(x)` arithmetic returns enum indexes, not byte offsets, which is correct only because write helpers translate later.

Test signals: compile with both CRU variants; enable dynamic/debug checks for WARNs in `__rzg2l_cru_write/read`; validate register writes against hardware manuals or tracepoints; stream on both variants to exercise `CRUnIE` vs `CRUnIE2`, `AMnMBS` vs `AMnMADRSL/H`, and stride-capable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/renesas/rzg2l-cru/rzg2l-cru-regs.h -->
