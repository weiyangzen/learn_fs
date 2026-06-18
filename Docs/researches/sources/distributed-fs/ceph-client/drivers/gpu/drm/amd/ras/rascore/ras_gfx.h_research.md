# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_gfx.h

Purpose: this header defines the generic GFX RAS dispatch interface used by the core and PSP layers.

Important types and APIs: `struct ras_gfx_ip_func` currently contains one operation, `get_ta_subblock()`, which translates a driver-visible GFX subblock and error type to a TA-compatible subblock. `struct ras_gfx` stores the configured GFX IP version and selected function table. Public functions are `ras_gfx_hw_init()`, `ras_gfx_hw_fini()`, and `ras_gfx_get_ta_subblock()`.

Control flow and state: no behavior is implemented here. State is the selected version/function pointer stored in the core context. There is no persistence.

Dependencies and integration: this header is consumed by core initialization and PSP TA error injection. It intentionally hides the large v9 subblock table behind the generic function table. Risks are null function-table use if callers skip or ignore `ras_gfx_hw_init()` failure, and API narrowness if future IP versions need more GFX RAS hooks. Test signals should compile both generic and v9-specific users and exercise error-type validation across the public `ras_gfx_get_ta_subblock()` wrapper.
