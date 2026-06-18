# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dcn21/hw_translate_dcn21.h

Purpose: DCN 2.1 translator declaration. Important API is `dal_hw_translate_dcn21_init(struct hw_translate *tr)`. There is no executable logic or persistence. Integration is through the common translator dispatcher for DCN 2.01/2.1. Dependencies are caller-visible `struct hw_translate`. Risks are prototype drift and missing target coverage. Tests are build/link plus GPIO service construction on DCN 2.1.
