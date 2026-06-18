# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_translate_dcn20.h

Purpose: DCN 2.0 translator declaration. Important API is `dal_hw_translate_dcn20_init(struct hw_translate *tr)`. There is no runtime control flow or persistence. Integration is through the common translator dispatcher for DCN 2.0. Dependencies are a visible `struct hw_translate`. Risks are signature drift and missing DCN2 build coverage. Tests are compile/link plus service creation on DCN 2.0.
