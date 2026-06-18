<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_config.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_config.py

## Purpose

`qemu_config.py` defines the shared data contract for architecture-specific KUnit QEMU boot configurations. The separate files under `qemu_configs/` instantiate this contract for each supported architecture.

## Important APIs, Types, and Functions

The only type is frozen dataclass `QemuArchParams` with fields `linux_arch`, `kconfig`, `qemu_arch`, `kernel_path`, `kernel_command_line`, `extra_qemu_params`, and optional `serial` defaulting to `stdio`. The immutability makes each architecture declaration stable after import.

## Control Flow

There is no active control flow beyond dataclass construction. KUnit code imports an architecture module, reads its `QEMU_ARCH` value, merges `kconfig` into the requested kernel configuration, builds the kernel at `kernel_path`, and starts the matching `qemu-system-*` binary with `kernel_command_line`, `serial`, and `extra_qemu_params`.

## State and Persistence Behavior

Instances are immutable and hold only boot metadata. They do not persist build products, QEMU state, or kernel output. Persistence happens in KUnit build directories and QEMU logs owned by the surrounding runner.

## Dependencies and Integration Points

The module depends on `dataclasses` and `typing.List`. It integrates with every file in `qemu_configs/`, with `kunit_kernel.LinuxSourceTree` architecture selection, and with CLI options such as `--arch`, `--qemu_config`, and `--qemu_args`.

## Risks and Edge Cases

Because `extra_qemu_params` is a mutable list stored inside a frozen dataclass, callers should not mutate it in place. Architecture modules must use kernel paths and console names that match the selected `linux_arch`; mismatches can lead to successful builds that never emit parseable KTAP output.

## Test Signals

CLI tests in `kunit_tool_test.py` validate that QEMU args and architecture options are forwarded into `LinuxSourceTree`. Integration smoke tests should import every `qemu_configs/*.py`, construct a KUnit kernel for the target architecture, and confirm KTAP appears on the declared serial console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_config.py -->
