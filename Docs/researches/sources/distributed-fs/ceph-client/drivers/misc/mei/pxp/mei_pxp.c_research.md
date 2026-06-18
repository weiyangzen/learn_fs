# sources/distributed-fs/ceph-client/drivers/misc/mei/pxp/mei_pxp.c

## Purpose
This MEI client driver bridges Intel graphics PXP/TEE operations to ME firmware. It exposes send, receive, and GSC scatter-gather command operations to i915 through the component framework and binds to the PAVP/PXP MEI client GUID.

## Important APIs, types, and functions
Core operations are `mei_pxp_send_message()`, `mei_pxp_receive_message()`, and `mei_pxp_gsc_command()`, published through `i915_pxp_component_ops`. Recovery helper `mei_pxp_reenable()` disables and re-enables the MEI client after selected send/receive failures. Component functions are `mei_component_master_bind()`, `mei_component_master_unbind()`, and `mei_pxp_component_match()`. Driver entry points are `mei_pxp_probe()` and `mei_pxp_remove()`.

## Control flow and state
Probe enables the MEI client, allocates an `i915_pxp_component`, creates a typed component match against Intel VGA/display PCI devices and `I915_COMPONENT_PXP`, stores component data in the MEI client, and registers as component master. Bind assigns ops and `tee_dev`, then binds all matching graphics components. Send and receive are synchronous MEI client operations with caller-supplied timeouts; on `-ENOMEM`, `-ENODEV`, or `-ETIME`, the channel is reenabled. Receive retries once after `-ENOMEM` with a short sleep.

## State and persistence behavior
Persistent runtime state is limited to the allocated component structure and enabled MEI client. PXP protocol messages and GSC scatterlists are transient. Removal unregisters the component master, frees component state, clears driver data, and disables the MEI client.

## Dependencies and integration points
It depends on MEI client bus APIs, Linux component framework, PCI matching, DRM i915 component headers, and `mei_pxp.h`. It integrates with i915 PXP code and GSC command transport through `mei_cldev_send_gsc_command()`.

## Risks and test signals
Risks include component topology matching for integrated vs discrete graphics, reenable masking deeper firmware failures, receive retry behavior around unclaimed responses, lifetime of `tee_dev`, and cleanup when component registration fails after client enable. Test signals include i915 component bind/unbind, PXP session negotiation, GSC command path, timeout/error recovery, remove while bound, and configurations with Xe/i915 dependency variants.
