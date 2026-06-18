# File Research: sources/block-storage/lvm2/libdm/make.tmpl.in

## Summary
Autoconf-generated make template shared by libdm/LVM2 subdirectories. It defines toolchain variables, install paths, warning flags, recursive targets, object/dependency rules, static/shared library rules, symbol export generation, cleaning, and optional analysis helpers.

## Main Responsibilities
- Imports configured tools, flags, libraries, prefixes, install directories, and feature settings.
- Establishes silent/verbose build behavior through `V`, `Q`, and `SHOW`.
- Sets compiler warnings, hardening flags, PIC/PIE options, debug flags, and include paths.
- Defines common recursive targets for subdirectories.
- Builds objects, dependency files, gettext template files, static libraries, and shared libraries.
- Installs shared libraries and plugins with compatibility symlinks.
- Generates linker version scripts from exported-symbol lists and optionally exported headers.
- Supports `cflow`, `cppcheck`, `gcc -fanalyzer`, gettext `.mo`, clean, and distclean targets.

## Key Targets and Variables
- Build flow: `all`, `$(SUBDIRS)`, `$(TARGETS)`, `$(LIB_STATIC)`, `$(LIB_SHARED).$(LIB_VERSION)`.
- Recursive helpers: `SIMPLE_RECURSIVE_TARGETS`, `SIMPLE_RECURSIVE_RULE`.
- Install: `install`, `install_device_mapper`, `install_lib_shared`, `install_dm_plugin`, `install_lvm2_plugin`.
- Analysis: `cflow`, `cppcheck`, `gccanalyze`.
- Cleanup: `cleandir`, `clean`, `distclean`.
- Symbol export: `.exported_symbols_generated`, `.export.sym`.
- Dependency inclusion gated by `@USE_TRACKING@`.

## Important Behavior
`CC` can be overridden by the environment, but the built-in default `cc` is replaced by the configured compiler. `CFLAGS` are protected against recursively re-adding `-fPIC`.

Shared library builds branch on `LIB_SUFFIX` for ELF `.so` versus Darwin `.dylib`. Static libraries are rebuilt with `ar rsv` after removing the old archive.

Full RELRO, `now`, `--as-needed`, and PIE flags are conditionally appended based on configure results and static/shared link mode.

Symbol script generation either builds a simple `Base` version or stitches together `.exported_symbols.*` files in version order, while checking that generated symbols match versioned symbol lists.

## State and Lifetime
This is a template consumed by configure to produce concrete Makefiles. Most values are `@...@` substitutions, and generated dependency files are optionally included for normal build goals.

## Risks
Global flags and include paths affect all subdirectories using the template. Symbol-list mismatches intentionally fail the build. The Makefile embeds platform-specific branches and old compiler warning switches that depend on configure checks.
