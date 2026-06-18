<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.h

## Purpose
`vs_bridge.h` defines the VeriSilicon bridge object and public bridge initializer used by the DRM core path. It is the small cross-file contract between bridge setup and CRTC/DC state.

## Important APIs, Types, and Functions
It defines `enum vs_bridge_output_interface` with DPI and DP values, `struct vs_bridge` containing DRM bridge, encoder, connector, CRTC, downstream bridge, and interface type, `drm_bridge_to_vs_bridge()`, and `vs_bridge_init()`.

## Control Flow
Consumers pass a DRM device and `struct vs_crtc` to `vs_bridge_init()`, then the bridge implementation allocates and attaches the encoder/bridge/connector for that output. The inline container helper is used by bridge callbacks to recover driver state.

## State and Persistence Behavior
The header declares persistent per-output bridge state but owns no memory itself. Instances are devm/drmm-managed by the implementation.

## Dependencies and Integration Points
It depends on DRM bridge, connector, and encoder definitions and forward-declares `struct vs_crtc`. `vs_drm.c` includes it to initialize outputs; `vs_bridge.c` implements the callbacks.

## Risks
The enum values match DT endpoint port indices used by `of_graph_get_remote_node()` and must not be changed casually. The object stores raw pointers whose lifetime is managed externally by DRM/devm helpers.

## Test Signals
Compile tests and bridge initialization for both DPI and DP outputs validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_bridge.h -->
