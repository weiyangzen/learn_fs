<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/deflate_xip_data.sh -->
# sources/distributed-fs/ceph-client/arch/arm/boot/deflate_xip_data.sh

## Purpose
This script post-processes an ARM XIP kernel image by replacing the file's trailing `.data` region with a gzip-compressed copy. It is used by the boot Makefile when both `CONFIG_XIP_KERNEL` and `CONFIG_XIP_DEFLATED_DATA` are enabled.

## Important APIs, Types, and Functions
Shell variables include `VMLINUX`, `XIPIMAGE`, `DD`, `__data_loc`, `_edata_loc`, `base_offset`, `data_start`, `data_end`, `file_end` and helper functions include `sym_val`. It relies on `$NM`, `$KGZIP`, `$CONFIG_SHELL`, `$srctree/scripts/file-size.sh`, and `dd status=none` with byte count/skip flags.

## Control Flow
The script enables `set -e`, optionally enables shell tracing for verbose builds, extracts `__data_loc`, `_edata_loc`, and `_xiprom` symbol values from `vmlinux`, converts them to file offsets, verifies `_edata_loc` matches the end of `xipImage`, installs a cleanup trap, copies bytes before `.data` into a temporary image, pipes the `.data` suffix through gzip, appends it, and atomically replaces the image.

## State and Persistence Behavior
The persistent artifact is the modified `xipImage`. Temporary state is `xipImage.tmp`, removed on signal-trap failure. The script intentionally mutates the image in place after validating symbol/file-size consistency.

## Dependencies and Integration Points
Integration is with `arch/arm/boot/Makefile` XIP image rules, the linked `vmlinux` symbol table, the generated raw `xipImage`, shell tools, `KGZIP`, and kernel boot code that knows how to inflate the compressed XIP data section.

## Risks
Risks include missing symbols, `NM` output format changes, a data section that is not the final file region, `dd` implementations without byte-count flags, interrupted writes before `mv`, and boot failures if the decompressor and image layout disagree about compressed `.data` placement.

## Test Signals
Build `make ARCH=arm xipImage` with XIP deflated data enabled, run with `KBUILD_VERBOSE=1`, verify the image shrinks/changes after `.data`, and boot the XIP image on a supported target. Negative tests should alter symbol expectations or truncate the image and confirm the script exits before replacement.

Source read size: 62 lines, 1663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/deflate_xip_data.sh -->
