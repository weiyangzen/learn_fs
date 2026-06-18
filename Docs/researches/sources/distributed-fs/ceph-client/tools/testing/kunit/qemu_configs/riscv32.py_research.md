<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/riscv32.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/riscv32.py

## Purpose

`riscv32.py` declares the KUnit QEMU boot profile for `riscv` kernels using QEMU target `riscv32`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='riscv'`, `qemu_arch='riscv32'`, `kernel_path='arch/riscv/boot/Image'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-machine virt`. The embedded Kconfig enables 32-bit nonportable RISC-V virt board with 8250/OF serial.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-riscv32`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `riscv32`, and Linux support for the declared `riscv` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `riscv`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/riscv32.py -->
