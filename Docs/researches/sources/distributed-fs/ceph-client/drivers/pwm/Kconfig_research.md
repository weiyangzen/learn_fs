# sources/distributed-fs/ceph-client/drivers/pwm/Kconfig

Purpose: defines the Linux PWM subsystem configuration menu and every controller-driver build symbol under `drivers/pwm`. It gates the generic PWM core, debug checks, optional PWM-as-GPIO support, C and Rust controller drivers, and per-platform dependencies.

Important APIs/types/functions: Kconfig symbols include `PWM`, `PWM_DEBUG`, `PWM_PROVIDE_GPIO`, all hardware driver symbols such as `PWM_AB8500`, `PWM_AIROHA`, `PWM_AXI_PWMGEN`, `PWM_DWC`, `PWM_CROS_EC`, and the internal `RUST_PWM_ABSTRACTIONS`. Dependency clauses bind drivers to subsystems including `HAS_IOMEM`, `COMMON_CLK`, `OF`, `ACPI`, `PCI`, `I2C`, `SPI`, `REGMAP_MMIO`, MFD parents, architecture families, and `COMPILE_TEST`.

Control flow: there is no runtime control flow. At configuration time `menuconfig PWM` enables the subtree, and each `tristate` determines whether a driver is built in, built as a module, or omitted. `select` clauses pull shared helpers such as `PWM_DWC_CORE`, `PWM_LPSS`, `REGMAP_MMIO`, or Rust abstractions.

State and persistence: state is the generated kernel `.config` and resulting Kbuild graph. Defaults are mostly explicit architecture defaults or unset symbols; no runtime state is created here.

Dependencies and integration: this is the build-time integration point between the PWM framework core, controller drivers, and platform subsystems. It must stay synchronized with `drivers/pwm/Makefile` object names and each driver's include/runtime dependencies.

Risks and test signals: missing dependencies surface as randconfig/allmodconfig build failures; overbroad dependencies can expose drivers on unsupported platforms. Test signals include `allmodconfig`, `allyesconfig`, `randconfig`, dependency-disabled configs, module/built-in combinations, and checks that selected internal symbols such as `PWM_DWC_CORE` and `PWM_LPSS` link correctly.
