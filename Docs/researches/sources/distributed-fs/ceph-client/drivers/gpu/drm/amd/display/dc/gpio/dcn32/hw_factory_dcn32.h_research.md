# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_factory_dcn32.h

Purpose: DCN 3.2-family factory declaration. Important API is `dal_hw_factory_dcn32_init(struct hw_factory *factory)`. The header has no executable behavior. Integration is through common factory cases for DCN 3.2, 3.21, 3.5, 3.51, and 3.6. Dependencies are `struct hw_factory` visibility. Risks are signature drift and per-generation topology differences hidden behind one init. Tests are build/link and service creation for every routed version.
