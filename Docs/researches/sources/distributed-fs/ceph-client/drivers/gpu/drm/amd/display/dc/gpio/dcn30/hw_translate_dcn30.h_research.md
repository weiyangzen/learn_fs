# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_translate_dcn30.h

Purpose: DCN 3.0 translator declaration. Important API is `dal_hw_translate_dcn30_init(struct hw_translate *tr)`. There is no runtime control flow or persistence. Integration is through the common translator dispatcher for DCN 3.0-family versions. Dependencies are caller-visible `struct hw_translate`. Risks are signature drift and insufficient per-version test coverage. Tests are build/link and GPIO service creation for each version routed here.
