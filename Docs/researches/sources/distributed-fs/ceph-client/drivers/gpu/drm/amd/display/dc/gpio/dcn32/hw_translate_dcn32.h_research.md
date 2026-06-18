# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn32/hw_translate_dcn32.h

Purpose: DCN 3.2-family translator declaration. Important API is `dal_hw_translate_dcn32_init(struct hw_translate *tr)`. It has no runtime state. Integration is through the common translator dispatcher for DCN 3.2, 3.21, 3.5, 3.51, and 3.6. Dependencies are caller-visible `struct hw_translate`. Risks are signature drift and hidden topology differences among routed versions. Tests are build/link and GPIO service creation for all routed generations.
