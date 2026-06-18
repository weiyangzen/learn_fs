# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/mei_gsc_proxy.c

## Purpose
`mei_gsc_proxy.c` is a MEI bus client that bridges Intel graphics GSC proxy component users to ME firmware through MEI send/receive operations.

## Important APIs, Types, and Functions
Important routines are `mei_gsc_proxy_send()`, `mei_gsc_proxy_recv()`, component master bind/unbind callbacks, `mei_gsc_proxy_component_match()`, `mei_gsc_proxy_probe()`, and `mei_gsc_proxy_remove()`. The MEI UUID is `MEI_UUID_GSC_PROXY`.

## Control Flow
Probe enables the MEI client, allocates an `i915_gsc_proxy_component`, builds a typed component match for an Intel VGA PCI device on bus 0 with `I915_COMPONENT_GSC_PROXY`, stores driver data, and registers a component master. Bind publishes MEI-backed send/recv ops and the MEI device pointer to the graphics component, then binds subcomponents. Remove unregisters the component master, frees state, clears driver data, and disables the MEI client.

## State and Persistence
State is the allocated `i915_gsc_proxy_component` stored as MEI client driver data, plus the enabled MEI connection. There is no persistence.

## Dependencies and Integration Points
Depends on MEI client bus APIs, Linux component framework, PCI device matching, DRM Intel i915 component interfaces, and graphics GSC proxy headers.

## Risks
The component match intentionally rejects discrete graphics by requiring PCI bus 0. Send/recv are thin wrappers, so MEI connection loss propagates directly. Allocation or component registration failure must disable the MEI client to avoid leaked connections.

## Test Signals
Signals are MEI UUID driver match, successful `mei_cldev_enable()`, component binding to integrated Intel VGA, functioning proxy send/recv, clean unbind/remove, and rejection of non-Intel/non-VGA/discrete or wrong subcomponent devices.
