# sources/distributed-fs/ceph-client/drivers/video/logo/Makefile

Purpose: build rules for Linux boot logo objects and the host-side `pnmtologo` converter. It maps Kconfig logo choices to generated C files and object files.

Important APIs, types, and functions: Make variables include `obj-$(CONFIG_LOGO*)`, `hostprogs := pnmtologo`, `quiet_cmd_logo`, `cmd_logo`, per-logo generated C targets, pattern rule for `%_clut224.c`, and `targets` for generated files.

Control flow: when a logo config is enabled, the relevant object is included. Generated C files depend on configured PNM files and the host `pnmtologo`; the kernel build invokes `pnmtologo -t <type> -n <logo-name> -o <output> <input>` through `if_changed`.

State and persistence: build-system state only. Generated C files are build artifacts, tracked in `targets`, not source runtime state.

Dependencies and integration points: depends on Kbuild hostprogs, config file path variables from Kconfig, and the `pnmtologo.c` converter. `logo.o` provides runtime selection through `fb_find_logo`.

Risks: custom logo file paths are direct dependencies and can break incremental builds if missing. The CLUT224 pattern rule assumes source file naming convention. Converter failures surface as build failures.

Test signals: run kernel build for each logo type; check generated `logo_linux_*.c` content, object inclusion, and incremental rebuild when PNM input changes.
