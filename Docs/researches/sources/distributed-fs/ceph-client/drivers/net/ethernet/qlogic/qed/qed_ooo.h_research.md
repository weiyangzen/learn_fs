# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.h

Purpose: Defines OOO buffer/isle/archipelago/history state and declares the OOO management API.

Important APIs/types/functions: `struct qed_ooo_buffer` records list linkage, virtual/physical RX buffer addresses, size, packet length, parse flags, VLAN, and placement offset. `struct qed_ooo_isle` holds an ordered buffer list. `struct qed_ooo_archipelago` holds per-connection isles. `struct qed_ooo_history` stores a circular CQE buffer. `struct qed_ooo_info` aggregates global free/ready/isle lists, arrays, counters, and CID base. The header declares all allocation, release, buffer movement, isle add/delete/join, and history functions, with disabled-config stubs.

Control flow: The header provides build-time selection through `CONFIG_QED_OOO`; disabled builds return `-EINVAL`, `NULL`, or no-op so callers can be compiled conditionally or guarded at runtime.

State and persistence: The structures describe state owned by `p_hwfn->p_ooo_info` and DMA-backed OOO receive buffers. There is no persistence outside memory and firmware event coordination.

Dependencies/integration: Includes QED core definitions, Linux list/slab/types, and references `struct ooo_opaque` from QED HSI.

Risks: The comment in the disabled branch still names iSCSI, but the config is `CONFIG_QED_OOO`. Consumers must not use return values from stubbed buffer getters without checking for `NULL`.

Test signals: Compile with OOO enabled/disabled, validate structure sizing assumptions, and verify all call sites handle stub returns cleanly.
