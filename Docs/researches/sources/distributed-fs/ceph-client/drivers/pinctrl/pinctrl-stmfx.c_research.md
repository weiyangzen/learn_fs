# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-stmfx.c

## Purpose
`pinctrl-stmfx.c` is the pinctrl, GPIO, pinconf, IRQ, and PM driver for the STMicroelectronics STMFX MFD GPIO expander. It exposes up to 24 GPIO/alternate-GPIO pins over the parent STMFX regmap and enables only the GPIO functions that are represented by `gpio-ranges`.

## Important APIs, Types, and Functions
`struct stmfx_pinctrl` holds the parent `struct stmfx`, pinctrl and gpiochip instances, a mutex used as IRQ bus lock, a valid GPIO mask, cached IRQ source/type/event/toggle arrays, and PM backup arrays. GPIO callbacks are `stmfx_gpio_get()`, `stmfx_gpio_set()`, direction get/input/output helpers, all operating on three banks of eight bits. Pinconf helpers map generic parameters to STMFX `GPIO_TYPE` and `GPIO_PUPD` semantics: `stmfx_pinconf_get()`, `stmfx_pinconf_set()`, and debug display. IRQ behavior is defined by `stmfx_pinctrl_irq_chip`, `stmfx_pinctrl_irq_set_type()`, `stmfx_pinctrl_irq_bus_sync_unlock()`, `stmfx_pinctrl_irq_thread_fn()`, and `stmfx_pinctrl_irq_toggle_trigger()`.

## Control Flow
Probe obtains the parent STMFX device, requires `gpio-ranges`, gets the platform IRQ, registers pinctrl with generic per-pin DT config mapping, enables pinctrl, registers a sleeping gpiochip with a threaded nested IRQ domain, enables STMFX GPIO/ALTGPIO functions according to available ranges, then requests the parent threaded IRQ. GPIO reads and writes use `GPIO_STATE`, `GPO_SET`, `GPO_CLR`, and `GPIO_DIR` registers. Pinconf get derives generic bias/drive/level answers from direction, type, pull, and output state.

IRQ type changes update cached arrays while holding the irq bus lock. Sync unlock writes event, type, and source arrays in bulk. For both-edge IRQs, the driver defers current-level sampling to sync-unlock because set-type may be atomic, then toggles the hardware edge polarity after each nested interrupt.

## State and Persistence
Hardware state is in STMFX registers accessed through the parent regmap. IRQ configuration is cached in `irq_gpi_src`, `irq_gpi_type`, `irq_gpi_evt`, and `irq_toggle_edge` so atomic irqchip callbacks avoid I2C/register accesses until bus sync. Suspend backs up GPIO state, direction, type, and pull registers; resume restores direction/type/pull/output state and IRQ event/type/source registers. Remove disables GPIO and alternate GPIO functions through the parent MFD function API.

## Dependencies and Integration Points
The driver depends on the STMFX MFD core (`stmfx_function_enable/disable`, `struct stmfx`, register definitions), regmap, platform IRQs, pinctrl utils, generic pinconf DT per-pin mapping, gpiochip nested threaded IRQ support, and PM sleep callbacks. Consumers use normal GPIO descriptors and pinctrl pin configuration; pin availability is governed by `gpio-ranges` rather than all 24 pins being blindly usable.

## Risks
The `IRQ_TYPE_EDGE_BOTH` non-toggle branch in `stmfx_pinctrl_irq_set_type()` clears `irq_toggle_edge[reg]` with `&= mask`, which preserves only the current bit instead of clearing it; this is suspicious and worth review. Both-edge support depends on reading GPIO state and rewriting trigger polarity after handling, so fast transitions can be missed. `stmfx_pinctrl_irq_thread_fn()` temporarily clears IRQ source enables by writing zeros, which reduces reentry but creates a window controlled by the parent interrupt behavior. Probe requires `gpio-ranges`, so missing DT range data is fatal. Restore writes backed-up `GPIO_STATE` through `GPO_SET`, which restores high outputs but does not explicitly clear low outputs unless prior direction/type state makes that harmless for the hardware.

## Test Signals
Test probe with 16-pin and 24-pin `gpio-ranges`, GPIO get/set/direction over all three register banks, generic pinconf bias/drive/level operations, nested IRQ mask/unmask/type programming, both-edge toggle behavior from both initial levels, suspend/resume register restoration, and function disable on remove. Fault injection should cover regmap bulk read/write failures, missing `gpio-ranges`, unavailable IRQ, and parent STMFX function enable errors.
