# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce60/hw_translate_dce60.h

Purpose: DCE 6.x translator declaration. Important API is `dal_hw_translate_dce60_init(struct hw_translate *tr)`. The header has no runtime behavior and no state. It depends on caller include order for `struct hw_translate`. Integration is via the common translator dispatcher under SI-supported DCE versions. Risks are prototype drift and missing SI build coverage. Tests are compile/link with `CONFIG_DRM_AMD_DC_SI` and GPIO service creation on DCE 6.x.
