# sources/distributed-fs/ceph-client/kernel/configs.c

## Purpose

`configs.c` embeds the compressed kernel build configuration into the kernel image and, when enabled, exposes it as `/proc/config.gz`.

## Important APIs, Types, and Functions

The file declares an assembly block containing `IKCFG_ST`, `kernel_config_data`, an `.incbin` of `kernel/config_data.gz`, `kernel_config_data_end`, and `IKCFG_ED`. When `CONFIG_IKCONFIG_PROC` is set, it defines `ikconfig_read_current()`, `config_gz_proc_ops`, `ikconfig_init()`, and `ikconfig_cleanup()`.

## Control Flow and State

The embedded config is static read-only data. Module init creates `/proc/config.gz`, points reads at the embedded byte range through `simple_read_from_buffer()`, and sets the proc entry size to the compressed config length. Module exit removes the proc entry.

## Dependencies and Integration Points

It depends on the build system producing `kernel/config_data.gz`, procfs, seq/read helpers, module init/exit, and `scripts/extract-ikconfig`, which looks for the `IKCFG_ST` and `IKCFG_ED` markers in binaries.

## Risks and Edge Cases

If the generated `kernel/config_data.gz` artifact is missing, the assembly include fails at build time. Runtime risk is low; proc entry creation can fail with `-ENOMEM`. Access is read-only, and the embedded data size is determined by linker symbols.

## Test Signals

Tests should build with and without `CONFIG_IKCONFIG_PROC`, verify `/proc/config.gz` exists only when configured, compare decompressed output to the build `.config`, run `scripts/extract-ikconfig` on the image/module, and test partial reads and seeks.
