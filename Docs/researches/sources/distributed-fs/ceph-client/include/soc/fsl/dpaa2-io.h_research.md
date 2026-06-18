# sources/distributed-fs/ceph-client/include/soc/fsl/dpaa2-io.h

Purpose: declares the DPAA2 DPIO service API for creating portals, handling notifications, enqueueing/dequeueing frame descriptors, buffer pool operations, stores, queue counts, and IRQ coalescing.

Important APIs and types: `struct dpaa2_io_desc` describes a portal, notification support, priority mode, CPU affinity, register mappings, DPIO id, QMan version, and clock. `struct dpaa2_io_notification_ctx` holds callbacks, CDAN/FQDAN identity, target CPU/DPIO id, QMan context, list node, and private data. APIs create/down DPIO objects, handle IRQs, select per-CPU services, register/deregister/rearm notifications, pull FQs/channels into stores, enqueue single/multiple descriptors to FQ/QD, acquire/release buffers, create/destroy/iterate stores, query FQ/BP counts, and tune IRQ coalescing/adaptive DIM.

Control flow: drivers select or create a DPIO service, register notification callbacks, pull work into stores, iterate `dpaa2_dq` results, enqueue completions/frames, and manage buffer pools through acquire/release.

State and persistence: runtime state includes portal mappings, notification lists, stores, interrupt/coalescing settings, and hardware queue state. No persistent storage is defined.

Dependencies and integration points: depends on DPAA2 FD/global headers, IRQ types, devices, cpumask, and list users. It is the core service layer for DPAA2 networking and accelerators.

Risks and test signals: risks include CPU affinity mismatch, notification rearm races, store exhaustion, enqueue batching partial failures, buffer-count overflows, and IRQ coalescing regressions. Test portal probe/teardown, FQ/channel pulls, notification callbacks, multi-enqueue paths, buffer acquire/release, query counts, and coalescing updates under traffic.
