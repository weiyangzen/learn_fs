# sources/distributed-fs/ceph-client/drivers/tty/vt/Makefile

Purpose: this Makefile defines the virtual-terminal build composition and generated-table rules. It builds VT core objects, console translation objects, and the host-side generator used to create the default console font Unicode table.

Important targets and variables: `FONTMAPFILE = cp437.uni`; `obj-$(CONFIG_VT)` includes `vt_ioctl.o`, `vc_screen.o`, `selection.o`, `keyboard.o`, `vt.o`, and `defkeymap.o`; `obj-$(CONFIG_CONSOLE_TRANSLATIONS)` includes `consolemap.o`, `consolemap_deftbl.o`, and `ucs.o`. `clean-files` removes generated C and UCS header tables. `hostprogs += conmakehash` builds the host utility. `cmd_conmk` invokes `$(obj)/conmakehash $< > $@` to generate `consolemap_deftbl.c`.

Control flow: when console translations are enabled, `consolemap_deftbl.c` depends on `cp437.uni` and the host `conmakehash` binary. Optional `GENERATE_KEYMAP` lets maintainers regenerate `defkeymap.c` from a map file via `loadkeys`. Optional `GENERATE_UCS_TABLES` regenerates width, recomposition, and fallback UCS headers with Python scripts, with value `2` passing `--full` to the recomposition generator. Normally shipped generated files are used instead.

State and persistence: generated files live under the object directory and are listed in `clean-files`. The Makefile itself encodes the default font map and build-time policy for generated versus shipped artifacts.

Dependencies and integration points: integrates with Kbuild object selection, host program compilation, `loadkeys`, `PYTHON3`, `conmakehash.c`, `consolemap.c`, `ucs.c`, and the VT Kconfig options `CONFIG_VT` and `CONFIG_CONSOLE_TRANSLATIONS`.

Risks: generated files must match shipped sources and runtime expectations. Requiring `loadkeys`, Python modules, or Unicode data during normal builds would break reproducibility, so regeneration remains opt-in. Wrong dependencies can leave stale UCS or consolemap tables. `FONTMAPFILE` changes alter the default hardware font mapping consumed by `consolemap.c`.

Test signals: clean and incremental Kbuild with VT enabled/disabled, console translations enabled/disabled, host `conmakehash` invocation, optional generated keymap and UCS table paths, `make clean` removing generated outputs, and reproducibility checks comparing regenerated shipped tables.
