# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.h

Purpose: Shared descriptor interface for Berlin-family pinctrl table drivers.

Important APIs/types/functions: defines `struct berlin_desc_function`, `struct berlin_desc_group`, and `struct berlin_pinctrl_desc`. Macros `BERLIN_PINCTRL_GROUP`, `BERLIN_PINCTRL_FUNCTION`, and `BERLIN_PINCTRL_FUNCTION_UNKNOWN` build null-terminated compound-literal function arrays. Declares `berlin_pinctrl_probe()` and `berlin_pinctrl_probe_regmap()`.

Control flow: per-SoC C files use macros to create descriptor arrays; the common core reads those descriptors to build runtime pinctrl function/group mappings and to compute regmap masks.

State and persistence: no runtime state in the header. Descriptor objects are static constants in each SoC file.

Dependencies/integration: requires platform_device and regmap types via included users; it is included by Berlin core and descriptor drivers.

Risks: compound literal lifetime is safe for file-scope static initializers, but moving macro use into block scope would create invalid dangling pointers. `u8` offset/bit fields cap descriptor values; current hardware tables fit.

Test signals: compile all Berlin descriptor users, check unknown groups terminate properly, and verify each `BERLIN_PINCTRL_GROUP` has at least the sentinel function.
