# sources/distributed-fs/ceph-client/include/drm/intel/i915_pxp_tee_interface.h

Purpose: declares the i915-to-TEE/GSC component interface for Protected Xe Path services.

Important APIs/types/functions: `struct i915_pxp_component_ops` contains module ownership plus `send()`, `recv()`, and `gsc_command()` callbacks. `send` and `recv` transfer opaque messages with timeouts. `gsc_command` sends a client/fence identified GSC command using input and output scatterlists. `struct i915_pxp_component` stores `tee_dev`, ops, and a mutex protecting them.

Control flow: i915 binds the component, serializes access with the mutex, sends PXP messages to the TEE device, receives replies, or submits scatter-gather GSC commands for protected content operations.

State and persistence: component state is the bound TEE device and ops table. PXP sessions and fences are maintained by provider firmware/driver state outside this header.

Dependencies and integration: depends on kernel device and mutex APIs and forward-declared `scatterlist`. Integrated by i915 PXP, TEE bus providers, and GSC command clients.

Risks and test signals: risks include timeout behavior, scatterlist sizing, stale component binding, and missing mutex discipline. Test bind/unbind, protected session setup/teardown, send/recv timeout and errno paths, and GSC command fence handling.
