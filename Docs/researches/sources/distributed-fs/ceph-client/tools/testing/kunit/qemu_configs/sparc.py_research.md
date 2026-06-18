<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sparc.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sparc.py

## Purpose

`sparc.py` declares the KUnit QEMU boot profile for `sparc` kernels using QEMU target `sparc`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='sparc'`, `qemu_arch='sparc'`, `kernel_path='arch/sparc/boot/zImage'`, `kernel_command_line='console=ttyS0 mem=256M'`, and extra QEMU parameters `-m 256`. The embedded Kconfig enables 32-bit SPARC with SUNZILOG console, KUnit fault test disabled, and 256 MiB memory cap.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-sparc`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `sparc`, and Linux support for the declared `sparc` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `sparc`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0 mem=256M`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sparc.py -->
