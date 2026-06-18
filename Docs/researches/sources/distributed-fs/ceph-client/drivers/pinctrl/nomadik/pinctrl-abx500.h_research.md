# sources/distributed-fs/ceph-client/drivers/pinctrl/nomadik/pinctrl-abx500.h

Purpose: this header defines the data model shared by the ABx500 common driver and AB8500/AB8505 SoC table files.

Important APIs, types, and functions: package IDs `PINCTRL_AB8500` and `PINCTRL_AB8505` select SoC data. `enum abx500_pin_func` defines default, ALT_A, ALT_B, and ALT_C modes. Pull and voltage enums describe supported GPIO electrical configuration values. `struct abx500_function`, `struct abx500_pingroup`, `struct alternate_functions`, `struct abx500_gpio_irq_cluster`, `struct abx500_pinrange`, and `struct abx500_pinctrl_soc_data` describe all static SoC inputs. Macros `ALTERNATE_FUNCTIONS()`, `GPIO_IRQ_CLUSTER()`, and `ABX500_PINRANGE()` initialize those tables.

Control flow: the common probe chooses a package ID and calls `abx500_pinctrl_ab8500_init()` or `abx500_pinctrl_ab8505_init()` to obtain a `struct abx500_pinctrl_soc_data`. If a table driver is disabled, inline stubs leave the pointer unchanged, allowing the core to report invalid SoC data instead of failing to link.

State and persistence behavior: the header has no runtime state. It defines table fields that the common driver treats as read-only, although the `alternate_functions` and IRQ cluster pointers are not declared const in the SoC descriptor.

Dependencies and integration points: dependencies include Linux types and pinctrl pin descriptors. It is the integration contract for Kconfig combinations where the common ABx500 core may be built with either, both, or neither SoC table object.

Risks and test signals: the alternate-function model must handle inconsistent ABx500 mux encodings, so per-pin values are easy to get wrong. GPIO range `offset` values are one-based to match ABx500 GPIO numbering, while gpiolib ranges are adjusted later. Test build combinations with disabled subdrivers, table bounds for `GPIO_MAX_NUMBER + 1`, and compiler coverage for const mismatches or missing init functions.
