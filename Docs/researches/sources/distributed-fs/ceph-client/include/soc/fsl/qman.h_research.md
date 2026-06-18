# sources/distributed-fs/ceph-client/include/soc/fsl/qman.h

Purpose: declares Freescale/NXP QMan hardware descriptor formats and the high-level portal, frame queue, congestion group, resource allocation, dequeue, enqueue, and coalescing APIs.

Important APIs and types: constants define channel IDs, interrupt sources, static dequeue pool masks, descriptor masks, FQ/CGR write-enable flags, and volatile dequeue flags. `struct qm_fd` and helpers encode 40-bit frame addresses, formats, offsets, and lengths. `struct qm_sg_entry` models SG entries. `struct qm_dqrr_entry` and `union qm_mr_entry` model dequeue and message-ring responses. `struct qm_fqd`, stashing/OAC helpers, taildrop helpers, `struct __qm_mc_cgr`, CGR threshold helpers, `struct qm_mcc_initfq`, and `struct qm_mcc_initcgr` build management commands. `struct qman_fq` and `struct qman_cgr` are caller-visible objects with dequeue/message/congestion callbacks. APIs manage portal IRQ sources, polling/static dequeue, FQ lifecycle, volatile dequeue, enqueue, FQID/pool/CGRID allocation, CGR lifecycle/query, probe status, and DQRR interrupt coalescing.

Control flow: drivers create/init/schedule FQs, enqueue `qm_fd` descriptors, receive DQRR callbacks, process ERN/FQ state messages, retire/OOS/destroy queues, and optionally use CGRs for congestion notifications. Portal code switches between interrupt-driven and polled sources and manages affine channels.

State and persistence: runtime state spans QMan portals, FQ objects, hardware FQD/CGR tables, ring entries, resource allocators, congestion state, and callback registrations. No persistent storage is defined.

Dependencies and integration points: depends on bitops, device/cpumask/list users, endian helpers from includers, and DPAA BMan/FMan/CAAM consumers. It is central to DPAA packet processing.

Risks and test signals: risks include 40-bit DMA address truncation, FQ state-machine races, callback reentrancy during retire, portal affinity misuse, taildrop/CGR threshold rounding errors, message-ring consumption bugs, and resource ID leaks. Test FQ create/init/schedule/enqueue/dequeue/retire/OOS/destroy, volatile dequeue completion, ERN paths, CGR congestion callbacks, resource allocator exhaustion/release, coalescing settings, and high-address descriptors.
