# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/reset-hi3660.c

Purpose: HiSilicon Hi3660 reset controller using a syscon phandle and two-cell reset specifiers.

Important APIs/types/functions: `struct hi3660_reset_controller`, `hi3660_reset_program_hw()`, `hi3660_reset_assert()`, `hi3660_reset_deassert()`, `hi3660_reset_dev()`, `hi3660_reset_xlate()`, and `hi3660_reset_probe()`.

Control flow: reset spec args are `(offset, bit)` and translate to `(offset << 8) | bit`. Assert writes the bit mask to `offset`; deassert writes to `offset + 4`; reset calls assert then deassert. Probe looks up `hisilicon,rst-syscon`, falls back to deprecated `hisi,rst-syscon`, and registers with two reset cells.

State and persistence: no cached reset state; writes are command-style register operations.

Dependencies and integration: platform driver uses OF, syscon, regmap, and `arch_initcall` for early availability.

Risks and test signals: no bit range validation in xlate beyond later register behavior; deprecated phandle support can hide DT drift. Test both phandle names, reset pulse ordering, and invalid bit/offset device tree cases.
