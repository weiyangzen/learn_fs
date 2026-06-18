# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_factory_dcn21.h

Purpose: DCN 2.1 factory declaration. Important API is `dal_hw_factory_dcn21_init(struct hw_factory *factory)`. It has no runtime state. Integration is via the common factory dispatcher for DCN 2.01 and 2.1. Dependencies are type visibility for `struct hw_factory`. Risks are signature drift and stale generation selection. Tests are build/link and GPIO service creation on DCN 2.1 families.
