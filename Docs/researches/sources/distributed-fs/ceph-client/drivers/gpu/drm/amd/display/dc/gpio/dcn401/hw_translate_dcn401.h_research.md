# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_translate_dcn401.h

Purpose: DCN 4.01 translator declaration. Important API is `dal_hw_translate_dcn401_init(struct hw_translate *tr)`. It has no runtime state. Integration is through the common translator dispatcher for DCN 4.01. Dependencies are caller-visible `struct hw_translate`. Risks are signature drift and register-generation churn. Tests are build/link and GPIO service creation on DCN 4.01.
