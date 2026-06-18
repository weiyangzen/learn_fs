# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn30/hw_factory_dcn30.h

Purpose: DCN 3.0-family factory declaration. Important API is `dal_hw_factory_dcn30_init(struct hw_factory *factory)`. It has no runtime state. Integration is through `hw_factory.c` for multiple DCN 3.x versions. Dependencies are include-order type visibility. Risks are signature drift and accidental use for a DCN generation with different pin topology. Tests are build/link plus service creation for every version routed to this init.
