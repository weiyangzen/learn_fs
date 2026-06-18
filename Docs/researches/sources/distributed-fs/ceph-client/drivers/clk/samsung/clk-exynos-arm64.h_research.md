# sources/distributed-fs/ceph-client/drivers/clk/samsung/clk-exynos-arm64.h

## Purpose

`clk-exynos-arm64.h` declares the shared arm64 Exynos CMU registration and PM helper API implemented by `clk-exynos-arm64.c`. SoC-specific Samsung clock drivers include it when registering `samsung_cmu_info` domains through the common arm64 setup path.

## Important APIs

- `exynos_arm64_register_cmu(struct device *dev, struct device_node *np, const struct samsung_cmu_info *cmu)` registers a CMU without PM-specific provider state.
- `exynos_arm64_register_cmu_pm(struct platform_device *pdev, bool set_manual)` registers a platform CMU with runtime/system PM support and optional initial register setup.
- `exynos_arm64_cmu_suspend(struct device *dev)` saves CMU/sysreg registers, applies suspend values, and disables the bus clock.
- `exynos_arm64_cmu_resume(struct device *dev)` re-enables clocks and restores CMU/sysreg registers.

## Control flow and integration

The header has no control flow. Early `CLK_OF_DECLARE` users can call `exynos_arm64_register_cmu(NULL, np, cmu)`, while platform-driver probes pass a real device or platform device to enable resource-managed mapping and runtime PM integration.

## State and persistence behavior

The header declares APIs that create persistent clock providers and, for PM registration, persistent per-device save/restore data. It defines no state itself.

## Dependencies

The header includes `clk.h` for `struct samsung_cmu_info` and references kernel device, device-node, and platform-device types.

## Risks and edge cases

- The PM helper boolean is named `set_manual` in the header but `init_clk_regs` in the C file, which can confuse readers about whether it controls manual mode specifically or broader initial register setup.
- Callers must choose simple versus PM registration correctly. A power-gated CMU registered through the simple helper can lose state across suspend.

## Test signals

Compile coverage validates signature consistency. Runtime validation comes from SoC drivers: successful registration for simple users and successful suspend/resume for PM users. New callers should be reviewed for correct boolean meaning.
