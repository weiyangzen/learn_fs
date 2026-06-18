<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bootconfig-data.S -->
# sources/distributed-fs/ceph-client/lib/bootconfig-data.S

## Purpose
Embeds a default bootconfig blob into the kernel image.

## APIs, Types, and Functions
Defines two global linker-visible symbols: `embedded_bootconfig_data` and `embedded_bootconfig_data_end`. Between them it includes the binary contents of `lib/default.bconf`.

## Control Flow, State, and Persistence
There is no executable code. The assembler places the data in `.init.rodata` with writable/alloc section flags as declared. At boot, bootconfig code can locate the embedded blob through the exported symbols and consume it during init; the data is init-time persistent only.

## Dependencies and Integration
Depends on `lib/Makefile` generating `default.bconf` from `CONFIG_BOOT_CONFIG_EMBED_FILE` and building this object when `CONFIG_BOOT_CONFIG_EMBED` is enabled. Integration is through the bootconfig parser and linker symbol resolution.

## Risks and Test Signals
Risks include missing generated `default.bconf`, empty embed file producing no effective defaults, section flag/linker-script mismatch, and consumers reading beyond the end symbol. Test signals include builds with and without `CONFIG_BOOT_CONFIG_EMBED_FILE`, `nm`/linker checks for both symbols, boot tests confirming embedded bootconfig options are applied, and init memory discard checks after parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bootconfig-data.S -->
