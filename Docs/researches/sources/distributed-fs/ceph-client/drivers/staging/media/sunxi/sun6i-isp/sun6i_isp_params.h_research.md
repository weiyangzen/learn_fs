# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/sun6i-isp/sun6i_isp_params.h

Purpose: declares params/meta-output structures and APIs for sun6i ISP runtime configuration.

Important APIs/types: `SUN6I_ISP_PARAMS_NAME`, `struct sun6i_isp_params_state` with queue, lock, pending buffer, configured flag, and streaming flag; `struct sun6i_isp_params` with video device, vb2 queue, mutex, media pad, and meta format. Functions declare params configuration, state update/complete, setup, and cleanup.

Control flow: no implementation; core interrupt code calls state completion/update and proc stream start calls configuration.

State and persistence: declares the state machine for parameter buffers and the `configured` flag that persists default module setup decisions.

Dependencies/integration: depends on V4L2 device types and shared sun6i ISP device/buffer definitions via include order.

Risks: queue comment is attached to `queue` while the spinlock is the actual lock; minor documentation ambiguity. Parameter state sequencing must stay aligned with capture sequence semantics.

Test signals: build coverage and params streaming/sequence tests.
