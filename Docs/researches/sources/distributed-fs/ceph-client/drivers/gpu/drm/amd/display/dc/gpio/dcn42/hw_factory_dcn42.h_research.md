# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn42/hw_factory_dcn42.h

Purpose: DCN 4.2 factory declaration. Important API is `dal_hw_factory_dcn42_init(struct hw_factory *factory)`. It has no runtime control flow or persistence. Integration is through the common factory dispatcher for DCN 4.2. Dependencies are `struct hw_factory` type visibility. Risks are signature drift and new-generation topology assumptions. Tests are build/link and GPIO service creation on DCN 4.2.
