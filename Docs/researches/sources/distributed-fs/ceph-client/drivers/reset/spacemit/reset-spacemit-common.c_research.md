# sources/distributed-fs/ceph-client/drivers/reset/spacemit/reset-spacemit-common.c

Purpose: shared SpacemiT auxiliary reset-controller implementation used by K1 and K3 reset table drivers.

Important APIs/types/functions: `spacemit_reset_update()` selects `ccu_reset_data` by ID, combines assert/deassert masks, and writes the selected value with `regmap_update_bits()`. `spacemit_reset_controller_register()` fills `rcdev`. Exported `spacemit_reset_probe()` converts the auxiliary device to `spacemit_ccu_adev`, obtains its regmap, stores `driver_data`, and registers the controller.

Control flow: SoC-specific auxiliary drivers share this probe; their auxiliary ID carries a `ccu_reset_controller_data` pointer. Runtime assert/deassert updates the configured CCU register masks.

State and persistence: controller state is device-managed; reset bits persist in the parent CCU registers.

Dependencies and integration: auxiliary bus, SpacemiT CCU helper API, regmap, reset-controller framework, and exported namespace `RESET_SPACEMIT`.

Risks and test signals: direct table indexing depends on reset core ID bounds and contiguous binding arrays. Test parent regmap lifetime, assert/deassert mask combinations, namespace import, and auxiliary driver data correctness.
