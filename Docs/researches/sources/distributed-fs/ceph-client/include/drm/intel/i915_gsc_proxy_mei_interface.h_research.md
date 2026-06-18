# sources/distributed-fs/ceph-client/include/drm/intel/i915_gsc_proxy_mei_interface.h

Purpose: defines the component interface between i915 and MEI drivers for forwarding GSC proxy messages between graphics firmware and management engine firmware.

Important APIs/types/functions: `struct i915_gsc_proxy_component_ops` holds an owning module plus `send()` and `recv()` callbacks. `struct i915_gsc_proxy_component` stores the MEI device pointer and ops table.

Control flow: i915 obtains the component, calls `send(dev, buf, size)` to transmit GSC-originated proxy data to ME firmware, and calls `recv(dev, buf, size)` to collect the ME response. Return values are byte counts or negative errno.

State and persistence: state is limited to the bound MEI device and stable ops pointer. Buffers are caller-managed transient payloads.

Dependencies and integration: depends on Linux types plus forward-declared `device` and `module`. Integrated through the component framework and MEI service drivers.

Risks and test signals: risks include short transfers, stale device/ops after unbind, module lifetime mistakes, and mismatched message sizes. Test component bind/unbind, send/recv failure paths, firmware timeout handling, and concurrent proxy traffic.
