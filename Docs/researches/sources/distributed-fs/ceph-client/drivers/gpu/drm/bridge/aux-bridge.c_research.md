# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-bridge.c

Purpose: Auxiliary-bus helper that creates a transparent DRM bridge device used to fill a bridge-chain position and attach to the next DT-described bridge.

Important APIs/types/functions: Exported API is `drm_aux_bridge_register(struct device *parent)`. Internal state is `struct drm_aux_bridge_data` with the DRM bridge, next bridge, and device pointer. Auxiliary driver probe is `drm_aux_bridge_probe`; bridge attach is `drm_aux_bridge_attach`.

Control flow: Registration allocates an `auxiliary_device`, assigns an ID through `IDA`, names it `aux_bridge`, inherits the parent's OF node, initializes and adds it, and installs a devm cleanup action that deletes/uninitializes it. Probe allocates bridge data, resolves the next bridge with `devm_drm_of_get_bridge(..., port 0, endpoint 0)`, sets passthrough format allowances, and devm-adds the bridge. Attach requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR` and attaches the next bridge after itself.

State and persistence: The IDA tracks allocated auxiliary IDs. The auxiliary device owns OF-node references and is freed in release. Bridge state is devm-managed and has no persistent storage.

Dependencies and integration: Depends on Linux auxiliary bus, OF node lifetime rules, DRM bridge helpers, and `drm/bridge/aux-bridge.h`. Intended for parent drivers that need a simple bridge placeholder.

Risks: Only connectorless chains are supported. OF node reference management must match auxiliary device init/add failure paths. The bridge performs no validation or mode ops, so downstream bridge behavior carries most display constraints.

Test signals: Register/unregister cleanup on parent detach, deferred next-bridge probe, attach with and without NO_CONNECTOR, IDA reuse, and OF refcount leak checks.
