# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama5.c

Purpose: registers SAMA5 device-tree machine descriptors and secure-cache setup.

Important APIs/types/functions: `sama5_l2c310_write_sec()` forwards L2C writes through `sam_smccc_call(SMC_CMD_L2X0SETUP1, ...)`; `sama5_secure_cache_init()` installs it in `outer_cache.write_sec`. Machine descriptors cover `atmel,sama5`, `atmel,sama5d4`, and `atmel,sama5d2`.

Control flow: DT machine matching calls SAMA5 PM init and optional secure cache init. The SAMA5D2 descriptor also initializes secure support via `sam_secure_init()`.

State and persistence: persistent effects are machine descriptor registration, outer-cache secure-write hook, and PM setup.

Dependencies and integration: integrates with `generic.h` PM init declarations, L2 cache controller hooks, secure SMCCC wrapper, and DT compatibles.

Risks: secure cache writes require firmware support; wrong compatible ordering can select the wrong PM path. Secure PM availability changes how `sama5d2_pm_init()` behaves.

Test signals: DT boot for SAMA5D3/D4/D2, L2 cache initialization under secure firmware, and suspend-mode registration messages.
