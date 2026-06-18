# sources/distributed-fs/ceph-client/include/uapi/drm/drm_ras.h

## Purpose

`drm_ras.h` is an auto-generated YNL UAPI header for the `drm-ras` generic netlink family. It exposes a small reliability, availability, and serviceability interface for discovering DRM RAS nodes and reading error counters associated with hardware or software components.

## Important APIs, Types, And Constants

`DRM_RAS_FAMILY_NAME` is `drm-ras`, and `DRM_RAS_FAMILY_VERSION` is `1`. `enum drm_ras_node_type` currently defines `DRM_RAS_NODE_TYPE_ERROR_COUNTER`. Node attributes are `NODE_ID`, `DEVICE_NAME`, `NODE_NAME`, and `NODE_TYPE`. Error-counter attributes are `NODE_ID`, `ERROR_ID`, `ERROR_NAME`, and `ERROR_VALUE`. Commands are `DRM_RAS_CMD_LIST_NODES` and `DRM_RAS_CMD_GET_ERROR_COUNTER`.

## Control Flow

The intended flow is netlink-based. Userspace discovers the generic netlink family, sends `LIST_NODES`, receives node records, and then sends `GET_ERROR_COUNTER` with node/error identifiers to read a named counter value. The header only defines enum IDs; generated YNL helpers and kernel netlink policy code perform message encoding and validation.

## State And Persistence

No state is stored in the header. Counter values are maintained by DRM drivers or subsystems. The header does not define whether counters reset on read, reset on driver reload, or persist across device reset, so monitoring code must treat those semantics as provider-specific.

## Dependencies And Integration Points

The file is generated from `Documentation/netlink/specs/drm_ras.yaml` and must stay synchronized with that spec. It integrates with Linux generic netlink, YNL-generated tooling, DRM RAS providers, telemetry collectors, and driver diagnostic utilities.

## Risks

Manual edits can diverge from the YAML source and be overwritten by regeneration. Attribute and command enum values are ABI-relevant. User space should ignore unknown future node types or attributes. Counter lifetime and monotonicity are not specified here, so analytics must avoid assuming too much from `ERROR_VALUE`.

## Test Signals

Useful tests include YNL regeneration diffs, generic netlink family discovery, schema/policy validation, list-node behavior with and without providers, get-counter for valid and invalid IDs, and compatibility tests where older userspace ignores future attributes.
