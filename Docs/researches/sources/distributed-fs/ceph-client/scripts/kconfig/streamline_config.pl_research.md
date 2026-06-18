# sources/distributed-fs/ceph-client/scripts/kconfig/streamline_config.pl

## Purpose
`streamline_config.pl` implements `localmodconfig`/`localyesconfig` style pruning. It reads an existing kernel config and currently loaded modules, maps modules to Kbuild objects and Kconfig symbols, preserves needed dependencies/selects, and emits a reduced config that disables unused modules.

## Important APIs, Types, and Functions
Major functions are `read_config()`, `read_kconfig()`, `convert_vars()`, `parse_config_depends()`, `parse_config_selects()`, `loop_depend()`, `loop_select()`, and `in_preserved_kconfigs()`. Important data maps include `%depends`, `%selects`, `%prompts`, `%objects`, `%config2kfile`, `%defaults`, `%modules`, `%configs`, `%orig_configs`, `%setconfigs`, and `%process_selects`.

Options are `--localmodconfig` and `--localyesconfig`. Inputs include source tree path, top Kconfig path, `LSMOD`, `LMC_KEEP`, `objtree`, and existing config locations such as `.config`, `/proc/config.gz`, `/boot/config-*`, `vmlinux`, or `configs.ko`.

## Control Flow
The script reads the base config, parses options, finds all `Makefile`/`Kbuild` files, optionally parses Kconfig dependencies and selects, maps `obj-$(CONFIG_*) += foo.o` lines to module names, reads loaded modules from `lsmod` or an override, marks configs required by loaded modules, repeatedly adds dependencies and selected hidden configs, then streams the original config while turning unused `=m` options into unset lines. It performs a final integrity check that loaded modules have at least one retained config.

## State and Persistence
The script emits the transformed config on stdout and diagnostics on stderr. It does not write `.config` itself. It may read host system state from `/proc`, `/boot`, loaded module lists, and source/build trees.

## Dependencies and Integration Points
It depends on Perl, `Getopt::Long`, `find`, `lsmod`, optional `scripts/extract-ikconfig`, Kbuild makefile syntax, and Kconfig syntax. It integrates with `make localmodconfig` and related targets.

## Risks and Edge Cases
The parsing is intentionally approximate and regex-based, so complex Kbuild/Kconfig constructs can be missed. Running against untrusted trees can execute helper commands from the configured search list. It only keeps dependencies already enabled as modules and avoids enabling unrelated options. It has special cases for `CONFIG_IKCONFIG`, module signing keys, and trusted keys to avoid broken follow-up builds. Module names and object names are normalized by replacing hyphens with underscores.

## Test Signals
Useful tests include fake `LSMOD` files, synthetic Makefiles/Kconfigs with dependencies/selects/defaults, `LMC_KEEP`, missing signing/trusted key files, and comparison against expected reduced configs for localmodconfig/localyesconfig.
