# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_colorop.c

## Purpose
`amdgpu_dm_colorop.c` advertises and constructs AMD's default DRM plane color pipeline. It exposes the supported transfer-function bitmasks and creates a linked set of `drm_colorop` objects matching the DC color pipeline consumed by `amdgpu_dm_color.c`.

## Important APIs, Types, And Functions
The file exports `amdgpu_dm_supported_degam_tfs`, `amdgpu_dm_supported_shaper_tfs`, and `amdgpu_dm_supported_blnd_tfs`, each as a bitmask of supported `DRM_COLOROP_1D_CURVE_*` values. `amdgpu_dm_initialize_default_pipeline` allocates up to ten colorops, initializes them with DRM helpers, links them with `drm_colorop_set_next_property`, and fills a `drm_prop_enum_list` entry naming the pipeline.

## Control Flow
Pipeline creation always starts with a degamma 1D curve, multiplier, and 3x4 CTM. If DC reports hardware 3D LUT or MPC preblend support, it appends shaper curve, shaper 1D LUT, and 3D LUT. It then appends blend 1D curve and blend 1D LUT. On any allocation or initialization failure, it logs allocation failures and destroys the colorop pipeline for the device.

## State And Persistence
State is DRM object state registered on the plane. The first colorop ID is stored in the enum list as the selectable pipeline type, and the pipeline name is dynamically allocated with `kasprintf`. There is no persistent storage outside the DRM object lifetime.

## Dependencies And Integration Points
The file depends on DRM plane/colorop/property helpers, AMDGPU device lookup, DC color caps, and constants from `amdgpu_dm.h`. It is tightly coupled to `amdgpu_dm_color.c`, whose parser assumes the exact operation order and skips optional shaper/3D-LUT entries based on the same capability predicate.

## Risks
Risks include chain-order drift between initialization and parser code, partial cleanup destroying more pipeline state than intended if multiple planes are being initialized, leaked `list->name` ownership if the DRM property layer does not assume it, and userspace-visible pipeline differences across hardware with and without 3D LUT support. The `MAX_COLOR_PIPELINE_OPS` ceiling must remain above the maximum constructed chain length.

## Test Signals
Useful tests inspect the plane `COLOR_PIPELINE` property, verify the advertised colorop order and supported curve masks, validate bypass behavior for every op, exercise initialization on hardware with and without 3D LUT support, force allocation/init failure paths in fault injection, and run colorop atomic commits that `amdgpu_dm_update_plane_color_mgmt` can parse successfully.
