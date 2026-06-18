# sources/distributed-fs/ceph-client/drivers/base/firmware_loader/builtin/Makefile

## Purpose
The builtin firmware Makefile generates assembly objects that embed `CONFIG_EXTRA_FIRMWARE` binary blobs and register them in the `.builtin_fw` section.

## Important APIs, Types, And Functions
Key variables are `fwdir`, `firmware`, `FWNAME`, `FWSTR`, `ASM_WORD`, `ASM_ALIGN`, and `PROGBITS`. The `filechk_fwbin` rule emits assembly with firmware data, name string, and a three-word metadata tuple.

## Control Flow, State, And Persistence
`fwdir` resolves absolute or source-tree-relative `CONFIG_EXTRA_FIRMWARE_DIR`. Each configured firmware name becomes a `.gen.S` and `.gen.o`; generated assembly includes the binary with `.incbin`, emits a stable name string, and appends name/data/size records to `.builtin_fw`. The object dependency points directly at the firmware file so missing or changed firmware triggers a rebuild.

## Dependencies, Integration Points, Risks, And Test Signals
This integrates with linker-provided `__start_builtin_fw` and `__end_builtin_fw` consumed by builtin `main.c`. Risks include name mangling collisions, firmware filenames containing commas or separators, architecture-specific `.section` syntax, and lack of compressed extra-firmware support. Test signals include embedding one or more blobs, absolute and relative directories, 32/64-bit builds, ARM section syntax, rebuilds after blob changes, and lookup by original firmware name.
