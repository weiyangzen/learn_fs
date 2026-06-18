<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona.h -->
# sources/distributed-fs/ceph-client/drivers/mfd/arizona.h

Purpose: declares private Arizona MFD internals shared between the transport, core, IRQ, and chip table files. Despite the old guard name `_WM5102_H`, it covers the wider Arizona family.

Important APIs and types: declares external regmap configurations for WM5102, WM5110, CS47L24, WM8997, and WM8998 transports; exported PM ops; regmap IRQ chips for each supported codec family; and internal lifecycle functions `arizona_dev_init`, `arizona_dev_exit`, `arizona_irq_init`, and `arizona_irq_exit`.

Control flow: bus drivers include this header to select regmap configs and call the core lifecycle functions. The core and IRQ implementation include it to access variant-specific patch/table objects compiled from other files.

State and persistence: the header owns no state. It expresses cross-translation-unit linkage for shared constant tables and lifecycle functions.

Dependencies and integration points: depends on `linux/of.h`, `linux/regmap.h`, and `linux/pm.h`, and assumes `struct arizona` is visible from the public Arizona core header in including files. It is the internal boundary among Arizona MFD compilation units.

Risks: one declaration pair, `wm8998_aod` and `wm8998_irq`, is non-const while other IRQ chips are const, so implementations must match this mutability. The guard and comment still mention WM5102, which can confuse maintainers. Missing declarations here break transport/core links rather than runtime behavior.

Test signals: compile/link coverage for all enabled Arizona Kconfig combinations, especially combinations with only one codec family enabled; sparse/const mismatch checks; and module dependency coverage between transport modules and table objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/arizona.h -->
