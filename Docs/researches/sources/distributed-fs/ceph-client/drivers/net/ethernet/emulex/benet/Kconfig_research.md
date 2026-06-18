# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/Kconfig

Purpose: defines configuration symbols for the Emulex/ServerEngines BladeEngine OneConnect `be2net` Ethernet driver, optional HWMON thermal reporting, and compile-time support for BE2, BE3, Lancer, and Skyhawk chipset families.

Important APIs/types/functions: `config BE2NET` is the main tristate driver symbol and depends on `PCI`. `config BE2NET_HWMON` enables thermal sensor exposure when both `BE2NET` and `HWMON` are available and prevents a built-in driver from depending on modular HWMON. `config BE2NET_BE2`, `BE2NET_BE3`, `BE2NET_LANCER`, and `BE2NET_SKYHAWK` are boolean chipset-family gates, each depending on `BE2NET` and defaulting to `y`. The final warning comment is visible if all chipset gates are disabled while `BE2NET` remains enabled.

Control flow: selecting `BE2NET` makes the driver buildable. The optional chipset booleans affect preprocessor branches in `be.h` and implementation files, such as whether `BE2_chip`, `BE3_chip`, `lancer_chip`, or `skyhawk_chip` can match devices. HWMON selection controls compilation/registration of temperature reporting paths in the driver.

State and persistence behavior: no runtime state is stored here. User choices persist in `.config` and shape the compiled driver feature set. Disabling all chip families can produce a built driver with no useful device support, which is explicitly warned about.

Dependencies/integration points: integrates with kbuild through `emulex/Makefile` and `benet/Makefile`, with Linux PCI support, HWMON core, and compile-time conditionals in `be.h`/be2net sources. The HWMON dependency `!(BE2NET=y && HWMON=m)` prevents invalid built-in-to-module references.

Risks: chipset booleans compile out device-family detection macros; an overly trimmed config can leave expected adapters unsupported. The warning is advisory only and does not prevent building a useless driver. HWMON default `y` may add sysfs sensor exposure when available, so thermal paths need to compile under both built-in and module combinations.

Test signals: generate configs for `BE2NET=y/m`, with each chipset option toggled, and ensure PCI ID matching and chip macros compile. Validate all-chipsets-disabled shows the warning. Build combinations of `BE2NET=y/m` with `HWMON=y/m/n` to confirm dependency constraints and HWMON code selection.
