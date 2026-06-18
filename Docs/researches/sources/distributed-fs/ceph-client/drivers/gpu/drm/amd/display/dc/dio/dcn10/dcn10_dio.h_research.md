# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn10/dcn10_dio.h

Purpose: Declares the DCN10 DIO memory power control wrapper.

Important APIs/types/functions: `TO_DCN10_DIO()` casts from `struct dio`. `DIO_REG_LIST_DCN10()` lists `DIO_MEM_PWR_CTRL`. `struct dcn_dio_registers`, `struct dcn_dio_shift`, and `struct dcn_dio_mask` expose the `I2C_LIGHT_SLEEP_FORCE` field. `struct dcn10_dio` embeds `struct dio`.

Control flow: Header-only; behavior is provided by `dcn10_dio.c`.

State/persistence: Stores base object and immutable register metadata pointers.

Dependencies/integration: Includes `dio.h` and is consumed by DCN resource construction.

Risks: Only one field is modeled, so any future use of other `DIO_MEM_PWR_CTRL` fields requires extending the mask/shift structs before using register helpers.

Test signals: Compile coverage and register metadata initialization for `DIO_MEM_PWR_CTRL`.
