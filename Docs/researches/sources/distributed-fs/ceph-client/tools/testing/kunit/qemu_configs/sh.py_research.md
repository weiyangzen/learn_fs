<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sh.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sh.py

## Purpose

`sh.py` declares the KUnit QEMU boot profile for `sh` kernels using QEMU target `sh4`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='sh'`, `qemu_arch='sh4'`, `kernel_path='arch/sh/boot/zImage'`, `kernel_command_line='console=ttySC1'`, and extra QEMU parameters `-machine r2d -serial mon:stdio; serial field is null`. The embedded Kconfig enables SH7751R RTS7751R2D Plus board with SCI serial and extended command line.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-sh4`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `sh4`, and Linux support for the declared `sh` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The module overrides the serial field to `null` while adding `-serial mon:stdio`; mismatches here can hide KTAP output from the parser. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `sh`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttySC1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sh.py -->
