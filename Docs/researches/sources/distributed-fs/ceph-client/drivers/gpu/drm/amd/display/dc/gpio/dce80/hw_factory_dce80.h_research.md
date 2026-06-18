# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/gpio/dce80/hw_factory_dce80.h

Purpose: DCE 8.x factory declaration. Important API is `dal_hw_factory_dce80_init(struct hw_factory *factory)`. It contains no executable control flow and stores no state. Integration is through `hw_factory.c` for DCE 8.x versions. Dependencies are include-order visibility of `struct hw_factory`. Risks are signature drift and missing build coverage for older DCE targets. Tests are compiler/link checks and GPIO service construction on DCE 8.0/8.1/8.3.
