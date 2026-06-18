# sources/distributed-fs/ceph-client/security/tomoyo/Makefile

## Purpose

This Makefile defines how the TOMOYO security module objects and generated built-in policy header are built. It lists all TOMOYO object files, enables context analysis for the directory, and converts policy `.conf` files into C string arrays included by `common.o`.

## Important APIs, types, and functions

`obj-y` lists the TOMOYO object set: `audit.o`, `common.o`, `condition.o`, `domain.o`, `environ.o`, `file.o`, `gc.o`, `group.o`, `load_policy.o`, `memory.o`, `mount.o`, `network.o`, `realpath.o`, `securityfs_if.o`, `tomoyo.o`, and `util.o`. `targets += builtin-policy.h` declares the generated header. The `cmd_policy` recipe emits `tomoyo_builtin_profile`, `tomoyo_builtin_exception_policy`, `tomoyo_builtin_domain_policy`, `tomoyo_builtin_manager`, and `tomoyo_builtin_stat` arrays from policy config files, escaping backslashes and double quotes and appending newline escapes. `$(obj)/common.o` depends on the generated header unless insecure built-in mode is enabled.

## Control flow

The build system evaluates the wildcard dependency over object-local `policy/*.conf` files and source default `policy/*.conf.default` files. When inputs change, `if_changed,policy` regenerates `builtin-policy.h`. For each known policy name, the recipe picks the first matching real config or default config, falls back to `/dev/null`, and writes a static `__initdata` character array. In normal configurations, `common.o` is rebuilt after the generated header is available.

## State and persistence behavior

Generated state is limited to `$(obj)/builtin-policy.h` in the build output tree. The embedded arrays become init-time kernel data and are not source-controlled. Because the recipe searches both object and source policy paths, a build can override defaults with generated or local object-tree policy files.

## Dependencies and integration points

It depends on Kbuild variables and commands such as `obj-y`, `targets`, `FORCE`, `quiet_cmd_*`, `cmd_*`, `$(call if_changed,...)`, `$(wildcard ...)`, `$(firstword ...)`, and `$(filter ...)`. It integrates with `common.o`, which consumes the built-in policy header, and with `CONFIG_SECURITY_TOMOYO_INSECURE_BUILTIN_SETTING`, which suppresses that dependency for fuzzing-oriented insecure builds.

## Risks and test signals

Risks include incorrect shell escaping of policy lines, stale generated headers when policy files change, unintended object-tree policy override, missing defaults silently becoming empty arrays, and insecure-mode builds not embedding expected policy. Test signals include clean and incremental builds, policy files containing quotes and backslashes, builds with and without object-tree policy overrides, builds under insecure built-in mode, and compile checks that `common.o` sees the generated symbols.
