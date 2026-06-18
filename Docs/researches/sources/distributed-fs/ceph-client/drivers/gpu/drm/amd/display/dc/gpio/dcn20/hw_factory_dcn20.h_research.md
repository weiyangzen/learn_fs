# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn20/hw_factory_dcn20.h

Purpose: DCN 2.0 factory declaration. Important API is `dal_hw_factory_dcn20_init(struct hw_factory *factory)`. There is no runtime control flow or state. Integration is the common factory dispatcher for DCN 2.0. Dependencies are caller-visible `struct hw_factory`. Risks are signature drift and missing DCN2 build coverage. Tests are compile/link and GPIO service construction on DCN 2.0.
