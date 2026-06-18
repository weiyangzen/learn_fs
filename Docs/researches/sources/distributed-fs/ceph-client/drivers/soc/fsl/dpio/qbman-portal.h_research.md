# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/qbman-portal.h

Purpose: internal DPAA2 QBMan portal API and data-structure definitions shared between the portal implementation and DPIO service layer.

Important APIs/types: defines QMan revisions, `struct qbman_swp_desc`, interrupt masks, pull/enqueue/release descriptors, result type constants, FQ management verbs, `struct qbman_swp` portal state, function pointers for portal variants, and inline wrappers such as `qbman_swp_enqueue()`, `qbman_swp_pull()`, `qbman_swp_release()`, and `qbman_swp_dqrr_next()`. It also defines result classifiers for DQ, SCN, FQDAN, CDAN, CSCN, BPSCN, CGCU, retirement, and park notifications.

Control flow and integration: service code builds descriptors using these helpers and then calls variant-dispatched inline wrappers. The header also provides inline FQ/CDAN convenience functions that call management command implementations.

State and persistence: `struct qbman_swp` is the central persisted software representation of a hardware portal, including valid-bit state, ring cursors, interrupt coalescing, and adaptive coalescing state.

Dependencies and risks: depends on `soc/fsl/dpaa2-fd.h` layouts. Risks include exposing mutable portal internals across C files and relying on external function pointers that can be switched by `qbman_swp_init()`.

Test signals: compile-time consumers in `dpio-service.c`, correct result classification in notification IRQ paths, and successful portal operations through the inline wrapper indirection.
