# sources/distributed-fs/ceph-client/sound/soc/meson/Makefile

Purpose: Maps Meson ASoC Kconfig symbols to composite module objects and single-driver objects. It defines which source files are linked into AIU, AXG FIFO/TDM/card/SPDIF/PDM, codec glue, G12A routing, and T9015 modules.

Important definitions: `snd-soc-meson-aiu-y` combines `aiu.o`, AIU codec control, encoders, and FIFO variants into one module. `snd-soc-meson-axg-fifo-y` provides the shared AXG FIFO helper, with FRDDR/TODDR as separate modules. TDM is split into formatter, interface, tdmin, and tdmout modules. Card utilities, codec glue, GX/AXG sound cards, G12A controls, and T9015 each have their own object lists. `obj-$(CONFIG_...)` lines bind the composite modules to Kconfig symbols.

Control flow: Kbuild uses the `*-y` object lists when the corresponding `obj-*` entry is enabled. Hidden helper symbols build common modules only when selected by public drivers.

State and persistence: No runtime state. Build output and module composition are determined by `.config`.

Dependencies and integration points: Mirrors symbol names from `Kconfig` and source-file boundaries in `sound/soc/meson`. Correct module composition is required for exported helper symbols such as AXG FIFO and TDM formatter routines.

Risks: Missing an object from a composite module causes unresolved symbols or absent DAI ops. Enabling helper modules independently without consumers can still produce modules with only exported helpers. New source files must be added both here and in Kconfig dependency chains.

Test signals: Incremental module builds for each symbol, link checks for `snd-soc-meson-aiu.ko`, `snd-soc-meson-axg-frddr.ko`, `snd-soc-meson-axg-tdmin.ko`, and allmodconfig link validation.
