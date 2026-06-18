# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_translate_dcn10.h

Purpose: DCN 1.0 translator declaration. Important API is `dal_hw_translate_dcn10_init(struct hw_translate *tr)`. It has no executable logic or persistence. Integration is via the common translator dispatcher for DCN 1.0/1.01. Dependencies are include-order type visibility. Risks are prototype drift and missing build coverage. Tests are compiler/link checks plus GPIO service creation on DCN 1.0 versions.
