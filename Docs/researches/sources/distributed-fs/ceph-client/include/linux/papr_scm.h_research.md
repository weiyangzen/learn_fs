# Research: sources/distributed-fs/ceph-client/include/linux/papr_scm.h

Purpose: `papr_scm.h` defines PAPR persistent-memory/SCM health and performance constants for IBM Power platform SCM devices.

Important APIs/types/functions: the file defines health bits such as `PAPR_PMEM_UNARMED`, `PAPR_PMEM_SHUTDOWN_DIRTY`, `PAPR_PMEM_EMPTY`, critical/fatal/unhealthy/non-critical health flags, encryption and scrub state, and `PAPR_PMEM_SAVE_FAILED`. It also groups those bits into masks like `PAPR_PMEM_UNARMED_MASK`, `PAPR_PMEM_BAD_SHUTDOWN_MASK`, `PAPR_PMEM_BAD_RESTORE_MASK`, `PAPR_PMEM_SMART_EVENT_MASK`, and `PAPR_PMEM_SAVE_MASK`.

Control flow and state: there is no executable control flow. The state represented is firmware-reported persistent-memory health, shutdown persistence status, restore status, and smart-event conditions. Bit numbering uses high-order PAPR convention with `1ULL << (63 - n)`.

Dependencies and integration points: used by PAPR SCM/NVDIMM drivers and user-visible health reporting paths. `PAPR_SCM_PERF_STATS_EYECATCHER` uses `__stringify`, so including contexts must provide the usual kernel macro environment.

Risks and test signals: risks are wrong bit interpretation, endian/bit-position confusion, and incomplete health-mask handling causing unsafe use of unarmed or dirty persistent memory. Tests should validate synthetic firmware bitmaps, smart event filtering, save-failure reporting, and perf stats version/eyecatcher compatibility.
