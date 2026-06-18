# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_translate_dce80.h

Purpose: DCE 8.x translator declaration. Important API is `dal_hw_translate_dce80_init(struct hw_translate *tr)`. There is no runtime state or control flow. Dependencies are a visible `struct hw_translate` declaration in including translation units. Integration is through the common translator dispatcher for DCE 8.x. Risks are prototype mismatch and stale include guards. Tests are build/link coverage plus service creation under DCE 8.x versions.
