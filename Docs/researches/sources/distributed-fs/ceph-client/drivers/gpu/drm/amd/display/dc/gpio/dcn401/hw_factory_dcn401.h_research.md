# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn401/hw_factory_dcn401.h

Purpose: DCN 4.01 factory declaration. Important API is `dal_hw_factory_dcn401_init(struct hw_factory *factory)`. It has no runtime control flow or persistence. Integration is via the common factory dispatcher for DCN 4.01. Dependencies are type visibility for `struct hw_factory`. Risks are prototype drift and generation-specific register churn. Tests are compile/link and GPIO service construction on DCN 4.01.
