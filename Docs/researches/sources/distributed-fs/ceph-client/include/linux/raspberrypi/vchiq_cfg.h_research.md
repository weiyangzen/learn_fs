# sources/distributed-fs/ceph-client/include/linux/raspberrypi/vchiq_cfg.h

Purpose: centralizes VCHIQ protocol versioning, shared-memory limits, slot/service counts, bulk queue sizing, and default debug/statistics enablement.

Important APIs and types: `VCHIQ_MAGIC`, `VCHIQ_VERSION`, `VCHIQ_VERSION_MIN`, and feature-version constants define compatibility. Resource constants include maximum states, services, slots, slots per side, current bulks, and service bulks. `VCHIQ_ENABLE_DEBUG` and `VCHIQ_ENABLE_STATS` default to enabled unless overridden.

Control flow: initialization writes and validates version/magic/resource values in shared memory; service open/version negotiation uses the compatibility constants; queue allocation and array sizing use max counts.

State and persistence: no state is stored here. Values shape shared-memory layout and runtime arrays.

Dependencies and integration points: depends on `VCHIQ_MAKE_FOURCC()` from `vchiq.h` and is consumed by `vchiq_core.h` and implementation files.

Risks and test signals: risks include incompatible version changes without updating `VERSION_MIN`, resource constants mismatching firmware, and debug/stat fields altering layout or overhead. Test version negotiation with firmware, max service/slot/bulk boundaries, debug/stat enabled and disabled builds, and shared-memory layout validation.
