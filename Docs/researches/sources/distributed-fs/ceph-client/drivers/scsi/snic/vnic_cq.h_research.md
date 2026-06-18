# sources/distributed-fs/ceph-client/drivers/scsi/snic/vnic_cq.h

Purpose: this header defines vNIC completion queue control registers, software CQ state, and the generic CQ service loop.

Important APIs, types, and functions: `struct vnic_cq_ctrl` maps the hardware CQ control register block. `struct vnic_cq` stores index, vNIC pointer, control MMIO pointer, descriptor ring, consumer index, and color. `svnic_cq_service()` decodes common CQ descriptors, loops while descriptor color differs from `last_color`, invokes a caller-supplied service callback, advances `to_clean`, toggles color at ring wrap, and stops at `work_to_do`.

Control flow: WQ ACK processing uses this generic service loop, while firmware completions use the SNIC-specific variant in `vnic_cq_fw.h`. The callback decides whether to continue or break.

State and persistence: state is runtime CQ ring and consumer color/index. No persistent state exists.

Dependencies and integration: includes `cq_desc.h` and `vnic_dev.h`. Allocation/init/free implementations are in `vnic_cq.c`; SNIC calls them from resource and cleanup paths.

Risks: `work_to_do` is unsigned, and callers pass `-1` to mean unlimited, which becomes a large unsigned value. That is intentional but should be understood. Correctness depends on hardware color-bit behavior and memory barriers in `cq_desc_dec()`.

Test signals: service zero, finite, and unlimited work budgets; callback break behavior; ring wrap; and stale descriptor avoidance under DMA stress.
