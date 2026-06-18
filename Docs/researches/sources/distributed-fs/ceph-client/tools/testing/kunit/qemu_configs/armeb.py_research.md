<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/armeb.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/armeb.py

## Purpose

`armeb.py` declares the KUnit QEMU boot profile for `arm` kernels using QEMU target `arm`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='arm'`, `qemu_arch='arm'`, `kernel_path='arch/arm/boot/zImage'`, `kernel_command_line='console=ttyAMA0'`, and extra QEMU parameters `-machine virt`. The embedded Kconfig enables big-endian ARM virt board with PL010/PL011 console support.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-arm`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `arm`, and Linux support for the declared `arm` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `arm`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyAMA0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/armeb.py -->
