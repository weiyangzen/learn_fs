# sources/distributed-fs/ceph-client/drivers/irqchip/irq-st.c

## Purpose
Programs STiH407 syscfg routing for selected Cortex-A9 IRQ/FIQ inputs. This is a syscfg helper rather than a full irqdomain provider: it enables and selects sources for two IRQ and two FIQ channels through a syscon regmap.

## Important APIs, Types, And Functions
`struct st_irq_syscfg` caches the syscon regmap, register offset, and computed configuration word. `st_irq_xlate()` translates DT binding device IDs into enable and channel-select bits. `st_irq_syscfg_enable()` parses `st,irq-device`, `st,fiq-device`, and `st,invert-ext`, then writes the masked syscfg register.

## Control Flow
Probe allocates state, obtains match-data register offset, looks up the `st,syscfg` phandle regmap, stores drvdata, and programs the syscfg. Resume rewrites the cached configuration using the same mask, restoring routing after system sleep.

## State And Persistence
The only persistent driver state is the computed `config` value; hardware state is the syscfg register. There is no dynamic interrupt allocation or per-line mask state.

## Dependencies And Integration Points
Depends on ST interrupt-controller DT binding constants, syscon/regmap, platform driver registration via `core_initcall`, and compatible `st,stih407-irq-syscfg`.

## Risks
Incorrect DT arrays silently route devices to the wrong IRQ/FIQ channel. The driver requires exactly two entries for both IRQ and FIQ device arrays. Because it rewrites a masked syscfg field, mask definitions must match hardware or unrelated syscfg bits could be altered.

## Test Signals
Validate probe with complete DT properties, invalid device IDs, resume restore, and functional routing of PMU, CTI, PL310, and external interrupt sources to the selected IRQ/FIQ channels.
