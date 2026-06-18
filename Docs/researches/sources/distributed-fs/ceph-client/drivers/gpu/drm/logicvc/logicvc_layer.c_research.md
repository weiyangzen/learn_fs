# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/logicvc_layer.c

Purpose: implements LogiCVC hardware layers as DRM planes, including DT layer parsing, format selection, atomic plane validation/update/disable, reserved-memory offset mapping for older IP, alpha, zpos, and layer list management.

Important APIs/types/functions: `logicvc_layers_init`, `logicvc_layers_attach_crtc`, `logicvc_layer_get_*`, `logicvc_layer_buffer_find_setup`, and internal `logicvc_plane_atomic_check/update/disable`.

Control flow: layer init walks the `layers` DT node, filters `layer` children, parses per-layer properties, resolves supported DRM formats from colorspace/depth/alpha, skips the final background layer if configured, initializes a primary or overlay plane, creates alpha/zpos properties, and appends it to `layers_list`. Atomic check rejects negative positions, verifies reserved-memory offset feasibility on IP without direct layer-address registers, and delegates no-scaling checks to DRM. Atomic update writes size, address or buffer/offset selectors, position, alpha, and control bits. Disable clears the layer control register.

State and persistence: each `struct logicvc_layer` stores parsed config, format table, OF node, DRM plane, list node, and hardware index. Hardware layer registers persist until changed.

Dependencies and integration points: depends on DRM atomic/plane/blend/fb DMA helpers, OF parsing helpers, LogiCVC caps/config, reserved memory base, regmap, and CRTC dimensions.

Risks and test signals: older IP address derivation is sensitive to reserved memory base, base offset, buffer offset, row stride, and pixel size. Plane positioning is only allowed for configurable non-final overlays. Test direct-address and offset-based IP versions, alpha modes, primary layer detection, background layer, unsupported formats, and page flips.
