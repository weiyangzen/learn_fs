# sources/distributed-fs/ceph-client/drivers/regulator/Makefile

Purpose: maps regulator Kconfig symbols to object files and core framework components for kbuild. It is the build integration point for all regulator drivers in this tree.

Important entries: `obj-$(CONFIG_REGULATOR)` builds core framework objects such as `core.o`, `dummy.o`, `helpers.o`, `devres.o`, and `irq_helpers.o`. `obj-$(CONFIG_OF)` adds `of_regulator.o`. Work-item mappings include `88pg86x.o`, `88pm800-regulator.o`, `88pm8607.o`, `88pm886-regulator.o`, `aat2870-regulator.o`, and `ab8500-ext.o ab8500.o`. `ccflags-$(CONFIG_REGULATOR_DEBUG) += -DDEBUG` enables debug compilation.

Control flow: kbuild expands each `obj-$()` line based on the final Kconfig value. Built-in symbols produce built-in objects; modular symbols produce module objects. Multiple objects on one line, such as `REGULATOR_AB8500`, are linked together under the same config decision.

State and persistence: no runtime state. Build products are generated according to `.config`.

Dependencies and integration: must remain synchronized with Kconfig symbols and source filenames. Core objects are prerequisites for individual drivers through regulator framework APIs. Some object names differ from config names, making this file the authoritative mapping.

Risks: stale or missing object entries make selected drivers silently absent from builds. The line `obj-$(CONFIG_REGULATOR_MT6315)  += mt6316-regulator.o` appears suspicious because there is a separate `REGULATOR_MT6316` Kconfig entry; this could build MT6316 under the wrong symbol. Multi-object config lines require both source files to compile for a symbol.

Test signals: inspect `make V=1` object selection for each relevant config, build `REGULATOR_AB8500` to ensure both `ab8500-ext.o` and `ab8500.o` compile, enable `REGULATOR_DEBUG` and verify `-DDEBUG`, and run `allmodconfig`/`allyesconfig` for stale mappings.
