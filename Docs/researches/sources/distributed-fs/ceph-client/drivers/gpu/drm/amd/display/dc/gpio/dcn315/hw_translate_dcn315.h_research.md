# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_translate_dcn315.h

Purpose: DCN 3.15 translator declaration. Important API is `dal_hw_translate_dcn315_init(struct hw_translate *tr)`. It has no runtime state or control flow. Integration is through the common translator dispatcher for DCN 3.15. Dependencies are caller-visible `struct hw_translate`. Risks are prototype drift and missing DCN 3.15 build coverage. Tests are compiler/link and GPIO service creation on DCN 3.15.
