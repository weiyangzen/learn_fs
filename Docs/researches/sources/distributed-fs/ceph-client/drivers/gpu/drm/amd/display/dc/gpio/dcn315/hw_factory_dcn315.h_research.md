# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn315/hw_factory_dcn315.h

Purpose: DCN 3.15 factory declaration. Important API is `dal_hw_factory_dcn315_init(struct hw_factory *factory)`. There is no runtime behavior. Integration is through `hw_factory.c` for `DCN_VERSION_3_15`. Dependencies are type visibility for `struct hw_factory`. Risks are prototype drift and missed DCN 3.15-specific topology tests. Test signals are compile/link and service creation for DCN 3.15.
