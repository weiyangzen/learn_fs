# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn10/hw_factory_dcn10.h

Purpose: DCN 1.0 factory declaration. Important API is `dal_hw_factory_dcn10_init(struct hw_factory *factory)`. The header has no runtime control flow or persistence. It integrates through `hw_factory.c` for DCN 1.0 and 1.01. Dependencies are type visibility for `struct hw_factory`. Risks are signature drift and missing include coverage. Tests are compile/link checks and service creation on DCN 1.0 targets.
