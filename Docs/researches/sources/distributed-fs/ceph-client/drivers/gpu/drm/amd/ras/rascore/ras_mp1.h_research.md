# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_mp1.h

Purpose: this header defines the MP1 RAS dispatch interface for querying and dumping valid MCA banks.

Important types and APIs: `struct ras_mp1_ip_func` contains `get_valid_bank_count()` and `dump_valid_bank()` operations. `struct ras_mp1` stores the MP1 IP version plus selected IP and system callback tables. Public APIs are `ras_mp1_hw_init()`, `ras_mp1_hw_fini()`, `ras_mp1_get_bank_count()`, and `ras_mp1_dump_bank()`.

Control flow and state: no behavior is implemented here. The state is embedded in `struct ras_core_context` and initialized by `ras_mp1.c`.

Dependencies and integration: it includes `ras.h` for core and error type definitions. ACA and firmware EEPROM paths depend on a valid MP1 system callback configuration. Risks are API contract ambiguity around `ecc_type`/`enum ras_err_type` values and unchecked null function pointers in generic wrappers. Test signals should compile all MP1 users, verify CE/DE share the CE message path in v13, and assert unsupported error types return `-EINVAL`.
