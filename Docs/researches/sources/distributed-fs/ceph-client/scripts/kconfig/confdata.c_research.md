# sources/distributed-fs/ceph-client/scripts/kconfig/confdata.c

## Purpose

`confdata.c` is the kconfig persistence layer. It reads user and generated configuration files, tracks whether the in-memory symbol graph differs from disk, writes `.config`/defconfig output, and emits generated build artifacts such as `include/config/auto.conf`, `include/generated/autoconf.h`, and `include/generated/rustc_cfg`.

## Important APIs, Types, and Functions

Public entry points include `conf_get_configname()`, `conf_read_simple()`, `conf_read()`, `conf_write_defconfig()`, `conf_write()`, `conf_write_autoconf()`, `conf_set_changed()`, `conf_get_changed()`, `conf_set_changed_callback()`, `conf_set_message_callback()`, and `conf_errors()`. Internal helpers handle filesystem safety and formatting: `make_parent_dir()`, `is_same()`, `conf_set_sym_val()`, `getline_stripped()`, `escape_string_value()`, `__print_symbol()`, `print_symbol_for_c()`, `print_symbol_for_rustccfg()`, `conf_write_autoconf_cmd()`, and `conf_touch_deps()`. `struct comment_style` abstracts generated-file headers, and global `autoconf_cmd` is written into the `.cmd` dependency file.

## Control Flow

Read flow starts with `conf_read()`, which clears the changed flag, delegates parsing of `.config` or default files to `conf_read_simple()`, recalculates `modules_sym` and all symbols, and marks the configuration dirty when saved user values no longer match calculated values or write eligibility. `conf_read_simple()` parses both `CONFIG_FOO=value` and `# CONFIG_FOO is not set`, validates values by symbol type, warns on malformed/unknown/reassigned lines, and reorders choice members so the last selected choice has priority.

Write flow is split by target. `conf_write()` traverses `rootmenu` depth-first, emits visible menu headings and writable non-choice symbols, writes to a temporary file unless `KCONFIG_OVERWRITECONFIG` is set, avoids replacing identical files, and renames the old file to `.old`. `conf_write_defconfig()` emits only user-changeable values that differ from defaults. `conf_write_autoconf()` writes the command dependency file, recalculates symbols, touches per-symbol dependency sentinels, then writes the C header, Rust cfg file, and finally `auto.conf` as the success marker.

## State and Persistence Behavior

The file owns the process-global changed flag, warning counters, message/change callbacks, and depfile prefix buffer. It persists configuration to user-selected paths, `.old` backups, generated headers/cfg, `auto.conf`, `auto.conf.cmd`, and empty include/config dependency files whose timestamps notify kbuild when individual symbols changed or disappeared. Environment variables alter paths and behavior: `KCONFIG_CONFIG`, `KCONFIG_AUTOCONFIG`, `KCONFIG_AUTOHEADER`, `KCONFIG_RUSTCCFG`, `KCONFIG_DEFCONFIG_LIST`, `KCONFIG_WERROR`, `KCONFIG_WARN_UNKNOWN_SYMBOLS`, and `KCONFIG_OVERWRITECONFIG`.

## Dependencies and Integration Points

It depends on the shared symbol/menu/expression model from `lkc.h`/`internal.h`, allocation helpers from `xalloc.h`, `zconf_fopen()` from the lexer, symbol APIs from `symbol.c`, and menu traversal from `menu.c`. It is called by command-line config tools, `mconf`, `gconf`, and build automation through the lkc API.

## Risks and Edge Cases

Path truncation and parent-directory creation errors can prevent writes; `is_same()` mmaps files and does not unmap before close, which is acceptable for a short-lived tool but worth noting. Generated files rely on rename ordering, with `auto.conf` intentionally last. String parsing differs for `S_DEF_AUTO` versus user config, so escaping bugs can cause mismatches. Unknown symbols in `auto.conf` trigger dependency touches; disabling that behavior would break incremental rebuilds. `KCONFIG_WERROR` promotes warnings into errors only through `conf_errors()`, so callers must check it.

## Test Signals

Good coverage includes kconfig parser tests for invalid values, duplicate assignments, unknown-symbol warnings, CRLF lines, choice override ordering, defconfig minimization, no-rewrite-on-identical-output, generated C/Rust/autoconf formatting, dependency touch behavior after symbol removal, and environment-variable path overrides.
