# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/hi6220_reset.c

Purpose: HiSilicon Hi6220 reset controller for peripheral, media, and always-on control blocks.

Important APIs/types/functions: `enum hi6220_reset_ctrl_type`, `struct hi6220_reset_data`, separate ops for peripheral/media/AO, `hi6220_peripheral_assert/deassert()`, `hi6220_media_assert/deassert()`, `hi6220_ao_assert/deassert()`, and `hi6220_reset_probe()`.

Control flow: OF match data selects controller type. Probe resolves the node as a syscon regmap, chooses ops and reset count, and registers the controller. Peripheral reset IDs encode bank in high bits and bit offset in low bits. AO assert/deassert sequences reset, isolation, and clocks in vendor-preserved order.

State and persistence: driver stores only regmap and controller metadata; hardware reset, isolation, and clock bits hold state.

Dependencies and integration: platform driver registered at `postcore_initcall`, using OF, syscon, regmap, and reset framework.

Risks and test signals: `PERIPH_MAX_INDEX` is a sparse encoded maximum rather than a simple count, and AO ordering is hardware-sensitive. Test all three compatibles, syscon lookup failure, peripheral bank addressing, AO sequencing, and early boot registration.
