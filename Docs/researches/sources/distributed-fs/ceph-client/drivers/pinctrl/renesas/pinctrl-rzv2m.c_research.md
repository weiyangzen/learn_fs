# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzv2m.c

## Purpose

`pinctrl-rzv2m.c` implements pinctrl, pinconf, and GPIO support for Renesas RZ/V2M (`renesas,r9a09g011-pinctrl`). It is derived from the RZ/G2L style but uses RZ/V2M-specific registers with write-enable bits in the upper word, 16-pin ports, a dedicated-pin pseudo-port, and drive-strength tables selected by voltage/group capability.

## Important APIs, Types, And Functions

The key static descriptions are `rzv2m_gpio_names`, `rzv2m_gpio_configs`, and `rzv2m_dedicated_pins`. `RZV2M_GPIO_PORT_PACK()` encodes pin count, register index, and capability bits; `RZV2M_SINGLE_PIN_PACK()` encodes dedicated pins using `RZV2M_DEDICATED_PORT_IDX`. `struct rzv2m_pinctrl_data` binds these tables, and `struct rzv2m_pinctrl` stores pinctrl/GPIO descriptors, the MMIO base, device pointer, spinlock, and DT group/function mutex.

`rzv2m_writel_we()` is the critical register helper for write-enable style registers. `rzv2m_pinctrl_set_pfc_mode()` masks input/output, writes the function select field in `PFSEL`, then unmasks input/output. DT parsing and generic pinctrl integration are handled by `rzv2m_dt_node_to_map()`, `rzv2m_dt_subnode_to_map()`, and `rzv2m_pinctrl_set_mux()`. Pinconf support is in `rzv2m_pinctrl_pinconf_get()` and `_set()`, with group wrappers. GPIO support is in `rzv2m_gpio_request()`, direction/value callbacks, `rzv2m_gpio_free()`, and `rzv2m_gpio_register()`.

## Control Flow

Probe allocates state, resolves match data, maps one MMIO resource, enables the clock with `devm_clk_get_enabled()`, initializes locks, and registers pinctrl/GPIO. Registration creates descriptors for all port pins plus seven dedicated pins, stores a per-pin copy of the packed config in `drv_data`, registers/enables pinctrl, validates `gpio-ranges`, and registers a GPIO chip.

DT mapping supports either `pinmux` or config-only `pins`. `pinmux` nodes become a generated generic group/function pair. Unlike RZ/G2L, the code parses configs in mux nodes but only creates config maps for `pins`; mux-node configs are not added to `nmaps`, so only config-only pin lists apply pinconf through DT mapping. Mux set iterates generated pins/PSEL values and writes the PFC sequence without per-pin validation in the mux path.

Pinconf resolves either a dedicated-pin encoding or a port-pin encoding. Bias reads/writes two-bit `PUPD` values, where hardware values map to pull-down, pull-up, or disable. Drive-strength-uA selects one of four tables based on capability group (`1.8V group2`, `1.8V group3`, `SWIO`, or `3.3V`) and writes a two-bit `DRV` field. Slew-rate uses `SR` with write-enable semantics.

GPIO request asks pinctrl core for the line and switches function to GPIO (`func 0`). Direction uses `OE` and `IE` write-enable registers, output value uses `DO`, input value uses `DI`, and free returns the line to input.

## State And Persistence

Runtime state is device-managed and not persisted across suspend by this driver. Hardware state is in `DO`, `OE`, `IE`, `PFSEL`, `DI`, `PUPD`, `DRV`, `SR`, and mask registers. The spinlock protects read-modify-write operations for pinconf registers, but several write-enable-only writes do not need readback. There is no IRQ support and no system PM callback in this file.

## Dependencies And Integration Points

The driver depends on Linux pinctrl, pinconf-generic, gpiolib, OF platform probing, one clock, one MMIO resource, and `dt-bindings/pinctrl/rzv2m-pinctrl.h`. It expects a correct `gpio-ranges` property whose count equals `n_port_pins`. It registers at `core_initcall` as `pinctrl-rzv2m`.

## Risks

Mux path lacks the explicit port/pin capability validation used by other Renesas drivers, so incorrect DT `pinmux` cells may program unexpected PFSEL fields. DT mux-node configs appear parsed but not mapped, which can surprise board authors who put pinconf next to `pinmux`. Bit-position mutation inside `rzv2m_pinctrl_pinconf_set()` multiplies `bit` by two for bias or drive-strength; if multiple configs for the same pin are applied in one call, later configs may use the mutated bit and target the wrong field. There is no suspend/resume restore, so low-power states that reset pin registers would lose configuration.

## Test Signals

Test mux state application for representative ports, config-only `pins` nodes for bias/drive/slew, applying multiple configs in one pinconf call, GPIO direction/value paths, invalid `gpio-ranges`, dedicated-pin pinconf, and unsupported drive strengths for each capability group.
