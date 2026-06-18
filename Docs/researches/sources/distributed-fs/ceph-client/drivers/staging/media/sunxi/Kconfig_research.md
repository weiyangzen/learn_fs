# Research: sources/distributed-fs/ceph-client/drivers/staging/media/sunxi/Kconfig

Purpose: top-level Kconfig menu gate for Allwinner sunXi staging media drivers.

Important APIs/types: `config VIDEO_SUNXI` is a bool depending on `ARCH_SUNXI || COMPILE_TEST`. When enabled, it sources the Cedrus VPU and sun6i ISP Kconfig files.

Control flow: Kconfig-only. Selecting `VIDEO_SUNXI` exposes child prompts but does not itself build a driver.

State and persistence: build configuration state only.

Dependencies/integration: integrates with `drivers/staging/media/Kconfig` and child directories `sunxi/cedrus` and `sunxi/sun6i-isp`.

Risks: disabling this parent hides all child drivers, which may surprise users because the help text notes it does not compile anything directly. `COMPILE_TEST` broadens build coverage beyond sunXi architecture.

Test signals: Kconfig generation with `ARCH_SUNXI`, non-sunxi `COMPILE_TEST`, and parent disabled should show or hide child symbols as expected.
