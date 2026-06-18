# sources/distributed-fs/ceph-client/drivers/reset/hisilicon/Kconfig

Purpose: Kconfig symbols for HiSilicon Hi3660 and Hi6220 reset controllers.

Important APIs/types/functions: `COMMON_RESET_HI3660` and `COMMON_RESET_HI6220` are tristate symbols depending on `ARCH_HISI` or `COMPILE_TEST`, defaulting to `ARCH_HISI`.

Control flow: configuration-time only; selected symbols build the matching reset driver object.

State and persistence: no runtime state; selections live in `.config`.

Dependencies and integration: both drivers integrate with syscon/regmap-based reset registers and the reset controller framework.

Risks and test signals: symbols named `COMMON_RESET_*` must stay aligned with the parent reset Makefile. Test HiSilicon defconfigs and compile-test builds with syscon/regmap dependencies.
