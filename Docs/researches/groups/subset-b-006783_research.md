# subset-b-006783 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_printer.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_printer.py

## Purpose

`kunit_printer.py` is the small output abstraction used by the KUnit Python tooling. It wraps a text stream with optional printing, terminal-aware ANSI coloring, and timestamped status output so parser, runner, and test code can share formatting behavior without each caller probing stdout directly.

## Important APIs, Types, and Functions

The main API is `Printer(print=True, output=sys.stdout)`. Its `print()` method writes a message only when printing is enabled, `print_with_timestamp()` prefixes the current local time as `HH:MM:SS`, and `red()`, `yellow()`, and `green()` conditionally wrap text in bold ANSI color escapes. `_color()` centralizes the `isatty()`-gated escape behavior, while `color_len()` returns the escape overhead by coloring an empty string. The module exports `stdout` for normal console output and `null_printer` for silent consumers.

## Control Flow

Construction decides whether color is possible: disabled printers never color, enabled printers color only if the output object reports `isatty()`. Printing then flows through `Printer.print()` so callers can pass a real or mock printer without branching. Color helpers are pure string transforms when color is enabled and no-ops otherwise.

## State and Persistence Behavior

State is limited to `_output`, `_print`, and `_use_color` on each `Printer` instance. The module has no persistent files or process-global counters beyond the two singleton printer instances. Timestamps are generated at call time and are not retained.

## Dependencies and Integration Points

It depends only on `datetime`, `sys`, and Python typing. It integrates with KUnit parser and tool tests, where `Printer.print` is mocked to assert user-visible summaries and error text. The `stdout` singleton is passed into parser calls in `kunit_tool_test.py`.

## Risks and Edge Cases

The constructor parameter named `print` shadows the builtin inside the method scope, though the method still calls the builtin from its own scope. Any output object used here must implement `isatty()` if color decisions are needed. `color_len()` is tied to the current color implementation and can return zero when color is disabled.

## Test Signals

Useful signals are parser tests that mock `Printer.print`, terminal versus non-terminal runner tests, and direct checks that disabled printers suppress writes and color escapes. Color behavior should be validated with fake output objects returning both `True` and `False` from `isatty()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_printer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_tool_test.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_tool_test.py

## Purpose

`kunit_tool_test.py` is the unit test suite for the KUnit Python command-line tooling. It exercises Kconfig parsing, KTAP/TAP parsing, parser laziness, Linux source-tree setup and QEMU/UML execution paths, JSON export, CLI argument plumbing, raw-output modes, timeout/build-directory handling, filter/list behavior, and isolated test execution.

## Important APIs, Types, and Functions

The file uses `unittest` and `unittest.mock` heavily. `setUpModule()` creates a temporary directory and locates `test_data`; `tearDownModule()` removes the temporary directory. `_test_data_path()` resolves fixture logs and configs. Test classes are `KconfigTest`, `KUnitParserTest`, `LineStreamTest`, `LinuxSourceTreeTest`, `KUnitJsonTest`, and `KUnitMainTest`. `line_stream_from_strs()` adapts lists to `kunit_parser.LineStream`, and `StrContains` lets mock assertions match substrings.

## Control Flow

The suite first validates low-level Kconfig read/write/subset semantics, then parses many fixture logs for success, failure, skipped suites, missing plans, no tests, kernel panic, prefixed printk output, KTAP attributes, and late test plans. Source-tree tests construct `LinuxSourceTree` with temporary config files and patched operations to avoid real kernel builds. CLI tests patch `kunit_kernel.LinuxSourceTree`, feed `kunit.main()` command arrays, and assert calls into `build_reconfig()`, `build_kernel()`, `run_kernel()`, and list helpers.

## State and Persistence Behavior

Persistent state is only temporary test data: `test_tmpdir`, temporary `.config`/`.kunitconfig` files, mocked environment variables, and generated output files such as KUnit run logs inside temporary build directories. The tests intentionally clear `os.environ` in main CLI tests and mock signal handling so host state does not leak into assertions.

## Dependencies and Integration Points

The suite imports `kunit_config`, `kunit_parser`, `kunit_kernel`, `kunit_json`, `kunit`, and `kunit_printer.stdout`. It integrates with fixture logs under `tools/testing/kunit/test_data`, Python subprocess behavior, terminal reset via `stty sane`, `KBUILD_OUTPUT`, QEMU argument handling, kernel argument forwarding, `--alltests`, `--kconfig_add`, `--run_isolated`, `--list_suites`, and `--list-opts`.

## Risks and Edge Cases

Tests depend on fixture log exactness and on mock call signatures matching production request dataclasses. Because many assertions check only plumbing, they can miss behavior inside patched dependencies. Raw-output tests assert absence of summary messages rather than full output fidelity. The terminal reset tests are careful to avoid invoking `stty` on non-TTY stdin; regressions there can corrupt interactive sessions.

## Test Signals

Running this file directly or through `run_checks.py` should pass without a kernel build except for code paths intentionally mocked. Strong signals include parser status/count assertions, JSON status mappings for FAIL/ERROR/SKIP/PASS, source-tree config conflict errors, non-mutating run-kernel args, correct `KBUILD_OUTPUT` defaulting, and isolated-suite/test calls derived from listed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_tool_test.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/mypy.ini -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/mypy.ini

## Purpose

`mypy.ini` defines the static type-checking policy for KUnit's Python tooling. It opts into strict mypy checking while preserving compatibility with Python versions older than 3.9.

## Important APIs, Types, and Functions

The file is configuration, not executable code. The `[mypy]` section sets `strict = True`, enabling mypy's broad family of strictness checks. It also sets `disable_error_code = type-arg`, allowing annotations that omit newer generic type arguments such as `subprocess.Popen[str]`.

## Control Flow

There is no runtime control flow. `run_checks.py` invokes `mypy --config-file mypy.ini --exclude _test.py$ --exclude qemu_configs/ .`, so this file controls type checking for production KUnit Python modules while excluding tests and architecture snippets.

## State and Persistence Behavior

The file persists local type-checking policy only. It does not create cache state itself, although mypy may create its own cache when invoked by developer tooling.

## Dependencies and Integration Points

It depends on the installed `mypy` executable and integrates with `run_checks.py`. The disabled `type-arg` error reflects the KUnit tool's desire to support Python 3.7+ syntax while still benefiting from strict type checks elsewhere.

## Risks and Edge Cases

Disabling `type-arg` weakens strict coverage for generic types and can hide imprecise container or subprocess annotations. Conversely, strict mode may reject changes that are runtime-correct but under-annotated. The exclusion of `qemu_configs/` means architecture config modules receive less type-check scrutiny.

## Test Signals

The main signal is a successful `mypy --config-file mypy.ini --exclude _test.py$ --exclude qemu_configs/ .` run from the KUnit tool directory. Regressions appear as new strict typing failures or use of syntax that breaks the Python versions the tool still supports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/mypy.ini -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/alpha.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/alpha.py

## Purpose

`alpha.py` declares the KUnit QEMU boot profile for `alpha` kernels using QEMU target `alpha`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='alpha'`, `qemu_arch='alpha'`, `kernel_path='arch/alpha/boot/vmlinux'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `none`. The embedded Kconfig enables 8250 serial console only.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-alpha`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `alpha`, and Linux support for the declared `alpha` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `alpha`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/alpha.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/arm.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/arm.py

## Purpose

`arm.py` declares the KUnit QEMU boot profile for `arm` kernels using QEMU target `arm`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='arm'`, `qemu_arch='arm'`, `kernel_path='arch/arm/boot/zImage'`, `kernel_command_line='console=ttyAMA0'`, and extra QEMU parameters `-machine virt`. The embedded Kconfig enables ARM virt board with PL010/PL011 console support.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/arm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/arm64.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/arm64.py

## Purpose

`arm64.py` declares the KUnit QEMU boot profile for `arm64` kernels using QEMU target `aarch64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='arm64'`, `qemu_arch='aarch64'`, `kernel_path='arch/arm64/boot/Image.gz'`, `kernel_command_line='console=ttyAMA0'`, and extra QEMU parameters `-machine virt -cpu max`. The embedded Kconfig enables AArch64 virt board with PL010/PL011 console support.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-aarch64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `aarch64`, and Linux support for the declared `arm64` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `arm64`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyAMA0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/arm64.py -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/i386.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/i386.py

## Purpose

`i386.py` declares the KUnit QEMU boot profile for `i386` kernels using QEMU target `i386`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='i386'`, `qemu_arch='i386'`, `kernel_path='arch/x86/boot/bzImage'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `none`. The embedded Kconfig enables 32-bit x86 with 8250 serial console.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-i386`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `i386`, and Linux support for the declared `i386` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `i386`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/i386.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/loongarch.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/loongarch.py

## Purpose

`loongarch.py` declares the KUnit QEMU boot profile for `loongarch` kernels using QEMU target `loongarch64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='loongarch'`, `qemu_arch='loongarch64'`, `kernel_path='arch/loongarch/boot/vmlinux.elf'`, `kernel_command_line='console=ttyS0 kunit_shutdown=poweroff'`, and extra QEMU parameters `-machine virt -device pvpanic-pci -cpu max`. The embedded Kconfig enables LoongArch virt machine, generic PCI host, pvpanic PCI, OF serial, EFI stub disabled.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-loongarch64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `loongarch64`, and Linux support for the declared `loongarch` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `loongarch`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0 kunit_shutdown=poweroff`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/loongarch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/m68k.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/m68k.py

## Purpose

`m68k.py` declares the KUnit QEMU boot profile for `m68k` kernels using QEMU target `m68k`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='m68k'`, `qemu_arch='m68k'`, `kernel_path='vmlinux'`, `kernel_command_line='console=hvc0'`, and extra QEMU parameters `-machine virt`. The embedded Kconfig enables m68k virt platform.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-m68k`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `m68k`, and Linux support for the declared `m68k` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `m68k`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=hvc0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/m68k.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips.py

## Purpose

`mips.py` declares the KUnit QEMU boot profile for `mips` kernels using QEMU target `mips`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='mips'`, `qemu_arch='mips'`, `kernel_path='vmlinuz'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M malta`. The embedded Kconfig enables 32-bit big-endian MIPS Malta with 8250 serial and syscon reset.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-mips`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `mips`, and Linux support for the declared `mips` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `mips`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips64.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips64.py

## Purpose

`mips64.py` declares the KUnit QEMU boot profile for `mips` kernels using QEMU target `mips64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='mips'`, `qemu_arch='mips64'`, `kernel_path='vmlinuz'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M malta -cpu 5KEc`. The embedded Kconfig enables 64-bit big-endian MIPS64 R2 Malta with 8250 serial and syscon reset.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-mips64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `mips64`, and Linux support for the declared `mips` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `mips`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips64.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips64el.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips64el.py

## Purpose

`mips64el.py` declares the KUnit QEMU boot profile for `mips` kernels using QEMU target `mips64el`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='mips'`, `qemu_arch='mips64el'`, `kernel_path='vmlinuz'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M malta -cpu 5KEc`. The embedded Kconfig enables 64-bit little-endian MIPS64 R2 Malta with 8250 serial and syscon reset.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-mips64el`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `mips64el`, and Linux support for the declared `mips` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `mips`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mips64el.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mipsel.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mipsel.py

## Purpose

`mipsel.py` declares the KUnit QEMU boot profile for `mips` kernels using QEMU target `mipsel`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='mips'`, `qemu_arch='mipsel'`, `kernel_path='vmlinuz'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M malta`. The embedded Kconfig enables 32-bit little-endian MIPS Malta with 8250 serial and syscon reset.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-mipsel`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `mipsel`, and Linux support for the declared `mips` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `mips`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/mipsel.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpc.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpc.py

## Purpose

`powerpc.py` declares the KUnit QEMU boot profile for `powerpc` kernels using QEMU target `ppc64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='powerpc'`, `qemu_arch='ppc64'`, `kernel_path='vmlinux'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M pseries -cpu power8`. The embedded Kconfig enables 64-bit big-endian pseries with 8250 and HVC console support.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-ppc64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `ppc64`, and Linux support for the declared `powerpc` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `powerpc`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpc32.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpc32.py

## Purpose

`powerpc32.py` declares the KUnit QEMU boot profile for `powerpc` kernels using QEMU target `ppc`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='powerpc'`, `qemu_arch='ppc'`, `kernel_path='vmlinux'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M g3beige -cpu max`. The embedded Kconfig enables 32-bit big-endian g3beige with CUDA and PMAC Zilog serial console.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-ppc`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `ppc`, and Linux support for the declared `powerpc` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `powerpc`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpc32.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpcle.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpcle.py

## Purpose

`powerpcle.py` declares the KUnit QEMU boot profile for `powerpc` kernels using QEMU target `ppc64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='powerpc'`, `qemu_arch='ppc64'`, `kernel_path='vmlinux'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-M pseries -cpu power8`. The embedded Kconfig enables 64-bit little-endian pseries with HVC console support.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-ppc64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `ppc64`, and Linux support for the declared `powerpc` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `powerpc`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/powerpcle.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/riscv.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/riscv.py

## Purpose

`riscv.py` declares the KUnit QEMU boot profile for `riscv` kernels using QEMU target `riscv64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='riscv'`, `qemu_arch='riscv64'`, `kernel_path='arch/riscv/boot/Image'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-machine virt -cpu rv64 -bios /usr/share/qemu/opensbi-riscv64-generic-fw_dynamic.bin`. The embedded Kconfig enables 64-bit RISC-V virt board with 8250/OF serial, early SBI console, and SBI v0.1.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-riscv64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `riscv64`, and Linux support for the declared `riscv` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

This module exits at import time if the OpenSBI firmware file is missing, so merely selecting the architecture can fail before KUnit builds anything. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `riscv`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/riscv.py -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/s390.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/s390.py

## Purpose

`s390.py` declares the KUnit QEMU boot profile for `s390` kernels using QEMU target `s390x`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='s390'`, `qemu_arch='s390x'`, `kernel_path='arch/s390/boot/bzImage'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-machine s390-ccw-virtio -cpu qemu`. The embedded Kconfig enables s390 ccw virtio machine with zEC12 tuning, NUMA, modules, and EXPERT enabled.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-s390x`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `s390x`, and Linux support for the declared `s390` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `s390`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/s390.py -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sparc64.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sparc64.py

## Purpose

`sparc64.py` declares the KUnit QEMU boot profile for `sparc` kernels using QEMU target `sparc64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='sparc'`, `qemu_arch='sparc64'`, `kernel_path='arch/sparc/boot/image'`, `kernel_command_line='console=ttyS0 kunit_shutdown=poweroff'`, and extra QEMU parameters `none`. The embedded Kconfig enables 64-bit SPARC with PCI and SUNSU serial console.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-sparc64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `sparc64`, and Linux support for the declared `sparc` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `sparc`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0 kunit_shutdown=poweroff`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/sparc64.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/x86_64.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/x86_64.py

## Purpose

`x86_64.py` declares the KUnit QEMU boot profile for `x86_64` kernels using QEMU target `x86_64`. It lets KUnit build a non-UML kernel and run it with architecture-specific console, machine, CPU, and firmware settings.

## Important APIs, Types, and Functions

The module imports `QemuArchParams` and exports one `QEMU_ARCH` instance. Its important fields are `linux_arch='x86_64'`, `qemu_arch='x86_64'`, `kernel_path='arch/x86/boot/bzImage'`, `kernel_command_line='console=ttyS0'`, and extra QEMU parameters `-bios qboot.rom`. The embedded Kconfig enables 64-bit x86 with 8250 serial console.

## Control Flow

Importing the module constructs the dataclass. KUnit's runner later consumes it to merge Kconfig fragments, locate the built kernel image, select `qemu-system-x86_64`, append the kernel command line, and route serial output back to the KTAP parser.

## State and Persistence Behavior

The file has no persistent mutable state. Its static `QEMU_ARCH` object describes build and boot state; actual kernel config files, build artifacts, and QEMU output live in the caller's build directory.

## Dependencies and Integration Points

It depends on the shared `qemu_config.py` contract, QEMU support for `x86_64`, and Linux support for the declared `x86_64` boot image. It integrates with KUnit `--arch` selection and any extra user `--qemu_args`.

## Risks and Edge Cases

The main risk is drift between kernel Kconfig, QEMU machine defaults, and the console selected for KTAP output. Firmware, BIOS, machine, or CPU options must exist on the host QEMU install. Console driver Kconfig and `kernel_command_line` must agree, otherwise KUnit may boot but report no tests.

## Test Signals

Useful validation imports the module, verifies the dataclass fields, builds a minimal KUnit kernel for `x86_64`, launches QEMU with the declared parameters, and confirms KTAP reaches the parser on `console=ttyS0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/qemu_configs/x86_64.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/run_checks.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/run_checks.py

## Purpose

`run_checks.py` is a developer convenience runner for validating KUnit Python tooling changes. It runs a bounded set of functional and static-analysis checks in parallel and reports pass, skip, failure, or timeout results.

## Important APIs, Types, and Functions

Global `commands` maps check names to argv sequences for `kunit_tool_test.py`, a KUnit smoke run over `lib/kunit`, `pytype *.py`, and mypy with `mypy.ini`. `necessary_deps` maps optional static analyzers to executable names. `main(argv)` validates that no arguments are supplied, schedules checks with `ThreadPoolExecutor`, reports outcomes, dumps captured failing output, and exits nonzero on failure. `run_cmd(argv)` wraps `subprocess.check_output()` with `cwd=ABS_TOOL_PATH`, combined stderr, and a five-minute timeout.

## Control Flow

The script skips pytype or mypy when the executable is absent, starts all remaining checks concurrently, then consumes futures as they complete. Exceptions are classified as timeout, called-process failure, or unexpected exception. Captured process output is indented under the failed check name to keep logs readable.

## State and Persistence Behavior

The script itself stores no persistent state. The smoke test may create `kunit_run_checks`, Python tools may create caches, and subprocesses may create build artifacts in the KUnit tool directory. The exit code is the primary state signal for CI or developer shells.

## Dependencies and Integration Points

It depends on Python concurrency/subprocess libraries, `mypy`, `pytype`, the local `kunit.py` CLI, and kernel build/QEMU prerequisites for the smoke test. It integrates with the strict typing policy in `mypy.ini` and the unit tests in `kunit_tool_test.py`.

## Risks and Edge Cases

Parallel execution can interleave expensive checks and increase CPU or I/O pressure. Optional analyzer skips can hide type regressions on machines without those tools. The smoke test depends on kernel build environment readiness and may fail for reasons unrelated to Python code. The script takes no arguments, so timeout and command set are not configurable from the CLI.

## Test Signals

A clean run prints `PASSED` for unit tests, smoke test, and installed analyzers, then exits zero. Expected skip lines for missing pytype or mypy are non-failures. A failing subprocess should print its captured output with `> ` indentation and exit with status 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/run_checks.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/Makefile

## Purpose

The memblock `Makefile` builds the user-space memblock simulator and test binary. It compiles a copy of the kernel `mm/memblock.c` together with tool-side stubs and memblock API tests under AddressSanitizer and UndefinedBehaviorSanitizer.

## Important APIs, Types, and Functions

Targets and variables define the build contract: `TARGETS = main`, `TEST_OFILES` includes allocation, helper, basic, NUMA, and exact-NID suites, `DEP_OFILES` includes `memblock.o`, `lib/slab.o`, `mmzone.o`, `slab.o`, and `cmdline.o`, and `EXTR_SRC = ../../../mm/memblock.c`. `BUILD=32` adds `-m32`; included `scripts/Makefile.include` processes user parameters such as `NUMA`, `MEMBLOCK_DEBUG`, and address-size options.

## Control Flow

The default `main` target links all object files. The `include` target creates local symlinks for kernel headers and x86 asm helpers, while `memblock.c` symlinks the real kernel implementation into the simulator directory. `clean` removes binaries, objects, and generated symlinks. `help` prints supported knobs.

## State and Persistence Behavior

Build state consists of object files, `main`, and symlinks under `linux/`, `asm/`, and `memblock.c`. Sanitizer instrumentation is part of every normal build. No test results are persisted by the Makefile itself.

## Dependencies and Integration Points

It depends on a kernel source tree layout, libasan, liburcu development packages, tool include directories, and shared scripts under `tools/scripts`. It integrates real kernel memblock code with user-space stubs in this directory and with test entrypoint `main.c`.

## Risks and Edge Cases

Symlink creation assumes relative paths remain valid. The simulator includes kernel C directly, so changes in kernel headers can require new stubs. Sanitizer flags may expose host compiler/runtime requirements. `BUILD=32` requires 32-bit toolchain and libraries.

## Test Signals

Successful `make` should produce `main`; running it should execute all memblock suites. `make clean` should remove generated symlinks and objects. Building with `NUMA=1`, `MEMBLOCK_DEBUG=1`, and `BUILD=32` exercises important alternate configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/asm/dma.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/asm/dma.h

## Purpose

`asm/dma.h` is an empty architecture header stub for the user-space memblock simulator. It satisfies include dependencies from kernel headers without modeling DMA behavior.

## Important APIs, Types, and Functions

The file only defines the `_TOOLS_DMA_H` include guard. It exports no macros, types, or functions.

## Control Flow

There is no control flow. Inclusion succeeds and contributes no declarations.

## State and Persistence Behavior

The header has no state and creates no persistent artifacts.

## Dependencies and Integration Points

It integrates with kernel headers pulled into the memblock simulator build. Its presence prevents missing-header failures when code includes `<asm/dma.h>`.

## Risks and Edge Cases

If future memblock dependencies start using DMA declarations, this empty stub will hide the missing model until compilation fails or behavior is silently untested.

## Test Signals

The build should compile without unresolved DMA symbols. Any new compile error involving DMA APIs is a signal that this stub needs a real simulator-side declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/asm/dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/internal.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/internal.h

## Purpose

`internal.h` supplies minimal `mm/internal.h`-style definitions needed to compile kernel `mm/memblock.c` in the user-space simulator. It replaces unrelated MM behavior with stubs while preserving the symbols memblock expects.

## Important APIs, Types, and Functions

It optionally enables `memblock_debug`, defines `pr_warn_ratelimited()` as `printf`, defines `K(x)`, declares `mirrored_kernelcore`, stubs `struct page`, `page_address()`, `virt_to_page()`, `memblock_free_pages()`, `accept_memory()`, `deferred_pages_enabled()`, `kasan_reset_tag()`, `__is_kernel()`, `init_deferred_page()`, and `__SetPageReserved()`. It declares `free_reserved_area()` and `free_reserved_page()` for simulator linkage.

## Control Flow

Most functions are no-ops or call `BUG()` for paths the simulator should not exercise. `for_each_valid_pfn` is reduced to a simple numeric loop. These definitions let memblock code compile while making accidental page-allocator paths obvious.

## State and Persistence Behavior

State is limited to global booleans such as `mirrored_kernelcore` and optional `memblock_debug`. It does not persist memory; real test memory state is managed by common test helpers and the memblock arrays.

## Dependencies and Integration Points

The header integrates kernel memblock implementation with user-space tests. It depends on simulator-provided `PAGE_SHIFT`, `BUG`, `printf`, `phys_addr_t`, and related kernel types from included tool headers.

## Risks and Edge Cases

The file defines `for_each_valid_pfn` twice, which is harmless only because the definitions are equivalent. BUG stubs are useful guardrails but can abort tests if new memblock paths legitimately need page conversion. No-op memory acceptance and deferred-page behavior mean those kernel paths are not functionally tested.

## Test Signals

Successful simulator compilation is the primary signal. Runtime should not hit `BUG()` through `page_address()` or `virt_to_page()`. Enabling `MEMBLOCK_DEBUG=1` should produce memblock debug printing without changing assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/lib/slab.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/lib/slab.c

## Purpose

`lib/slab.c` provides the tiny slab-availability hook needed by kernel code compiled into the memblock simulator.

## Important APIs, Types, and Functions

It defines global `enum slab_state slab_state` and implements `slab_is_available()` as `slab_state >= UP`.

## Control Flow

The only control flow is the comparison against the `UP` slab state. Callers can treat allocation helpers as available only after the simulated slab state reaches that level.

## State and Persistence Behavior

`slab_state` is process-global simulator state. It is not persisted beyond a test process and is reset only by normal process startup or explicit test code.

## Dependencies and Integration Points

It includes `<linux/slab.h>` from the tool/kernel header set and links with memblock code paths that test slab availability.

## Risks and Edge Cases

The implementation does not model slab allocation itself. Any kernel code that needs real slab caches would require additional simulator support.

## Test Signals

Build/link success and paths that query `slab_is_available()` are the relevant signals. Tests should continue to pass with the default `slab_state` expected by the simulator harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/lib/slab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kernel.h

## Purpose

This shim `linux/kernel.h` lets the memblock simulator include common kernel utility declarations from the tools include tree while adding user-space headers and local stubs needed by memblock tests.

## Important APIs, Types, and Functions

It wraps the upstream tools kernel header and includes `errno`, C string support, local `printk`, linkage, kconfig, string, and ctype headers. It exports no new functions itself.

## Control Flow

There is no runtime control flow. Inclusion aggregates the headers expected by compiled kernel code.

## State and Persistence Behavior

The header has no state and creates no artifacts.

## Dependencies and Integration Points

It depends on `../../include/linux/kernel.h` and local simulator headers under `tools/testing/memblock/linux`. It is an integration point between real kernel includes and the constrained user-space memblock build.

## Risks and Edge Cases

Header-order changes can expose missing declarations or conflicting definitions between libc and kernel-style headers. Since it acts as an aggregate, unrelated kernel include changes can break this simulator layer.

## Test Signals

The signal is successful compilation of memblock simulator sources that include `<linux/kernel.h>`, especially after kernel header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kmemleak.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kmemleak.h

## Purpose

`linux/kmemleak.h` stubs kmemleak hooks for the user-space memblock simulator. Memblock can notify kmemleak in the kernel, but the simulator does not run the kernel leak detector.

## Important APIs, Types, and Functions

The header defines no-op `kmemleak_free_part_phys(phys, size)`, no-op `kmemleak_alloc_phys(phys, size, gfp)`, and no-op `dump_stack()`.

## Control Flow

All functions return immediately. They preserve call compatibility while intentionally discarding leak-tracking side effects.

## State and Persistence Behavior

No kmemleak state is stored. Alloc/free events are not persisted or inspected by this simulator layer.

## Dependencies and Integration Points

It relies on kernel-style `phys_addr_t`, `size_t`, and `gfp_t` declarations from other included headers. It integrates with `mm/memblock.c` call sites that would normally inform kmemleak.

## Risks and Edge Cases

Leak detector behavior is outside test coverage. Bugs involving kmemleak notification ordering, flags, or stack dumps will not be caught by these memblock simulator tests.

## Test Signals

Compilation without kmemleak symbols and sanitizer-clean execution are expected. New memblock code that depends on kmemleak return values would require this stub to change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kmemleak.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/memory_hotplug.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/memory_hotplug.h

## Purpose

`linux/memory_hotplug.h` provides the small memory-hotplug surface needed by memblock code in the simulator, mainly the movable-node enablement query.

## Important APIs, Types, and Functions

It includes NUMA, PFN, cache, and type headers; declares external `bool movable_node_enabled`; and defines `movable_node_is_enabled()` to return that global.

## Control Flow

The only behavior is reading `movable_node_enabled`. Memblock code can branch on the same API it uses in the kernel.

## State and Persistence Behavior

`movable_node_enabled` is external process-local state. The header does not define or persist it.

## Dependencies and Integration Points

It integrates with memblock code and `linux/mmzone.h` in this simulator. Test setup may control `movable_node_enabled` through command-line or common helpers.

## Risks and Edge Cases

The simulator models only the boolean gate, not real memory hotplug operations. Hotplug-specific page lifecycle, zone growth, or online/offline transitions are outside this test harness.

## Test Signals

Build success and tests that toggle movable-node behavior through common memblock parameters are the useful signals. New unresolved references to hotplug APIs indicate the shim is incomplete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/memory_hotplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mmzone.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mmzone.h

## Purpose

`linux/mmzone.h` supplies a compact zone and node model for compiling and testing memblock code outside the kernel.

## Important APIs, Types, and Functions

It declares `first_online_pgdat()` and `next_online_pgdat()`, defines `for_each_online_pgdat`, `enum zone_type`, `MAX_NR_ZONES`, `MAX_PAGE_ORDER`, `MAX_ORDER_NR_PAGES`, pageblock alignment helpers, `struct zone` with `managed_pages`, and `pg_data_t` with a `node_zones` array.

## Control Flow

Iteration over online pgdats is delegated to the two functions implemented in `mmzone.c`; in this simulator they currently return `NULL`, so loops over online pgdats do not execute.

## State and Persistence Behavior

The structs describe process-local simulated node/zone state only. No persistent zone data exists outside test memory structures.

## Dependencies and Integration Points

It includes atomic and memory-hotplug shims and is consumed by memblock code paths that refer to zones, pageblocks, or online nodes. It links with `mmzone.c` for iterator functions.

## Risks and Edge Cases

The model is intentionally minimal. Any memblock changes requiring real zone types, multiple zones, managed page accounting, or online pgdat iteration may compile but remain under-modeled.

## Test Signals

Successful compilation and tests that do not unexpectedly require online pgdat iteration are the main signals. New assertions around pageblock alignment should use the constants defined here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mmzone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mutex.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mutex.h

## Purpose

`linux/mutex.h` is a simulator mutex shim. It provides enough syntax for kernel code that declares mutexes or uses guard-style mutex helpers, without implementing locking.

## Important APIs, Types, and Functions

It defines `DEFINE_MUTEX(name)` as an `int`, provides `dummy_mutex_guard(int *name)`, and maps `guard(mutex)` to the dummy guard symbol.

## Control Flow

There is no locking behavior. Guard expressions compile to dummy functions, so critical sections are not serialized.

## State and Persistence Behavior

Mutexes become integer variables with no lock state. The simulator is single-process and does not persist synchronization state.

## Dependencies and Integration Points

It integrates with kernel code included in the memblock simulator that expects mutex macros. The tests themselves run single-threaded, so real locking is unnecessary for current coverage.

## Risks and Edge Cases

Concurrency behavior is not tested. If future simulator code becomes multi-threaded or depends on lock ordering, this shim will be insufficient.

## Test Signals

Compilation is the key signal. Any runtime race tests or lockdep-like expectations would require a real mutex model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/mutex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/printk.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/printk.h

## Purpose

`linux/printk.h` maps kernel logging macros to user-space `printf` for the memblock simulator.

## Important APIs, Types, and Functions

It includes `stdio.h` and `asm/bug.h`, suppresses GCC format warnings around the mapping, defines `printk` as `printf`, and aliases `pr_info`, `pr_debug`, `pr_cont`, `pr_err`, and `pr_warn` to `printk`.

## Control Flow

Logging call sites execute as direct `printf` calls. The diagnostic pragma suppresses known format mismatches from memblock debug calls using kernel integer types.

## State and Persistence Behavior

There is no logging state beyond stdout/stderr buffering controlled by the C runtime. Messages are not persisted unless the caller redirects process output.

## Dependencies and Integration Points

It integrates kernel memblock logging with the simulator's console output and common test verbosity controls. `MEMBLOCK_DEBUG=1` can route additional memblock debug text through these macros.

## Risks and Edge Cases

The file appears to use `#pragma GCC diagnostic push` twice instead of a final pop, which can leave warning state suppressed for subsequent includes in the translation unit. Mapping all severities to `printf` loses kernel log levels and rate limiting.

## Test Signals

Builds should not fail on memblock debug format strings. Verbose/debug simulator runs should print expected messages without changing allocation assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/printk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/string_helpers.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/string_helpers.h

## Purpose

`linux/string_helpers.h` is a placeholder shim for the memblock simulator. It satisfies include dependencies without implementing string helper routines that current tests do not use.

## Important APIs, Types, and Functions

The file only defines `_LINUX_STRING_HELPERS_H_`. It intentionally omits `string_get_size()` and other helpers.

## Control Flow

There is no control flow.

## State and Persistence Behavior

The header has no state and persists nothing.

## Dependencies and Integration Points

It integrates with kernel headers or memblock code that include `<linux/string_helpers.h>` during simulator compilation.

## Risks and Edge Cases

If future memblock paths call a string helper, the simulator will fail to link or compile until a stub or real implementation is added.

## Test Signals

Successful compilation proves no current path needs these helpers. Any unresolved string helper symbol is the cue to extend this shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/string_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/main.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/main.c

## Purpose

`main.c` is the entrypoint for the memblock simulator test binary. It parses command-line options and runs the memblock API suites in a fixed order.

## Important APIs, Types, and Functions

`main(argc, argv)` includes headers for basic, allocation, helper allocation, NUMA allocation, exact-NID allocation, and common test utilities. It calls `parse_args()`, `memblock_basic_checks()`, `memblock_alloc_checks()`, `memblock_alloc_helpers_checks()`, `memblock_alloc_nid_checks()`, and `memblock_alloc_exact_nid_checks()`.

## Control Flow

Execution is linear: parse options, run each suite, return zero if assertions do not abort. Each suite handles its own prefix stack, dummy memory initialization, memblock reset, and cleanup.

## State and Persistence Behavior

Global simulator state such as memblock region arrays, dummy physical memory, prefix state, and option flags is initialized and reset by the called suites. The entrypoint itself persists nothing.

## Dependencies and Integration Points

It links all test object files named in the Makefile. It is the integration point that proves the real `mm/memblock.c` can coexist with simulator stubs and every selected test suite.

## Risks and Edge Cases

Because all suites run in one process, leaked global state from an earlier suite can affect later suites. The fixed order can hide order dependencies unless individual suites reset state thoroughly.

## Test Signals

Running `./main` should complete without assertion failure and return zero. Running with verbose/debug/NUMA build options should show the suite prefixes and still pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/mmzone.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/mmzone.c

## Purpose

`mmzone.c` implements the minimal node/zone functions declared by the simulator `linux/mmzone.h`.

## Important APIs, Types, and Functions

It defines `first_online_pgdat()` and `next_online_pgdat()` to return `NULL`, and `atomic_long_set(atomic_long_t *v, long i)` as an empty stub.

## Control Flow

Online-node iteration immediately terminates because the first iterator returns `NULL`. Atomic set call sites compile but do not alter storage.

## State and Persistence Behavior

No pgdat or atomic state is maintained by this file. It deliberately avoids modeling kernel zone lists.

## Dependencies and Integration Points

It includes `<linux/mmzone.h>` and links with memblock code that references online pgdat helpers or atomic zone counters.

## Risks and Edge Cases

Any future test that expects managed page accounting or online pgdat traversal will be under-modeled. The empty `atomic_long_set()` can hide state updates if memblock starts relying on its side effects in tested paths.

## Test Signals

Current tests should pass without iterating online pgdats. New failures or missing side effects around zone accounting indicate this shim needs a fuller implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/mmzone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.c

## Purpose

`alloc_api.c` tests the generic `memblock_alloc()` and `memblock_alloc_raw()` APIs against a simulated physical memory map. It verifies placement, alignment, zeroing behavior, reservation merging, and failure cases for both top-down and bottom-up allocation modes.

## Important APIs, Types, and Functions

`get_memblock_alloc_name()` labels the active API, and `run_memblock_alloc()` dispatches to raw or zeroing allocation based on `alloc_test_flags`. Scenario functions cover simple allocation, disjoint reservations, before/after merges, second fit, in-between full merge, small gaps, all memory reserved, insufficient space, limited exact space, no registered memory, and too-large allocations. `memblock_alloc_checks_internal(flags)` runs all scenarios for one API mode; `memblock_alloc_checks()` runs normal and raw modes.

## Control Flow

Each test resets or sets up memblock, optionally reserves regions, calls the selected allocation API, then asserts returned pointer, memory contents, `memblock.reserved` entry base/size/count, and `total_size`. Wrapper functions run directional variants by toggling `memblock_set_bottom_up()` or using `run_top_down()` and `run_bottom_up()`.

## State and Persistence Behavior

The suite manipulates global `memblock`, reservation arrays, allocation direction, and dummy physical memory. It initializes dummy memory at suite start and cleans it at suite end. Raw allocations are expected to preserve nonzero memory content, while normal allocations are expected to zero memory.

## Dependencies and Integration Points

It depends on `alloc_api.h`, `common.h`, the real memblock implementation, and common helpers such as `setup_memblock()`, `dummy_physical_memory_init()`, `assert_mem_content()`, and prefix/test reporting. It is called from `main.c`.

## Risks and Edge Cases

Assertions assume precise reserved-region ordering and merge behavior, so legitimate changes to memblock sorting or alignment policy require test updates. The tests use small synthetic memory sizes, which may miss overflow or large-map behavior. Raw memory checks depend on dummy memory being pre-poisoned.

## Test Signals

Passing signals include correct top-down placement near the end of DRAM, bottom-up placement at the start, proper merging with adjacent reservations, NULL on impossible allocations, accurate `reserved.cnt` and `total_size`, zeroed normal allocations, and nonzero raw allocations under sanitizers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.h

## Purpose

`alloc_api.h` declares the public entrypoint for the generic memblock allocation tests.

## Important APIs, Types, and Functions

It includes `common.h` and declares `int memblock_alloc_checks(void);`.

## Control Flow

The header has no control flow. `main.c` calls the declared function to run normal and raw allocation suites.

## State and Persistence Behavior

It stores no state. The implementation manages memblock and dummy memory state.

## Dependencies and Integration Points

It integrates `alloc_api.c` with the simulator entrypoint and shared test helpers.

## Risks and Edge Cases

The narrow interface hides individual scenarios from other translation units; adding selective execution would require new declarations.

## Test Signals

Successful compilation and linkage of `main.o` against `alloc_api.o` confirm the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.c

## Purpose

`alloc_exact_nid_api.c` tests `memblock_alloc_exact_nid_raw()`, the strict NUMA-node allocator. Unlike the try-NID API, exact-NID allocation must not fall back to other nodes when the requested node or range cannot satisfy the allocation.

## Important APIs, Types, and Functions

The file defines an eight-node `node_fractions` layout and many NUMA scenarios for top-down and bottom-up modes: simple node allocation, partial reservations, split ranges where lower limits are dropped, no-overlap-low cases, small node failure, fully reserved node failure, partial-reservation failure, split-range-high failure, no-overlap-high failure, large-region failure, full merge between border reservations, and split-all-reserved failure. `__memblock_alloc_exact_nid_numa_checks()` runs exact NUMA scenarios; `memblock_alloc_exact_nid_checks()` also invokes shared exact-NID range checks from `alloc_nid_api.c`.

## Control Flow

Each scenario calls `setup_numa_memblock(node_fractions)`, computes requested node/range boundaries, optionally reserves blocking regions, calls `memblock_alloc_exact_nid_raw(size, align, min, max, nid)`, and asserts either a node-local reservation or NULL. Wrappers run symmetric top-down and bottom-up expectations where direction changes placement but not strict node selection.

## State and Persistence Behavior

The suite uses global memblock node metadata, reserved arrays, allocation direction, and dummy physical memory. `memblock_alloc_exact_nid_checks()` resets attributes, initializes dummy memory, executes range and NUMA checks, then cleans up.

## Dependencies and Integration Points

It includes `alloc_exact_nid_api.h` and `alloc_nid_api.h` because exact-NID range checks reuse the generic range-test machinery with `TEST_F_RAW | TEST_F_EXACT`. It depends on `CONFIG_NUMA` gating in the header and common NUMA setup helpers.

## Risks and Edge Cases

Strict no-fallback semantics are easy to regress if shared try-NID code paths change. Some tests deliberately expect lower range limits to be dropped while preserving exact-node behavior, which is subtle. The synthetic NUMA layout may not cover all node interleavings or large address boundaries.

## Test Signals

Strong signals are NULL for requested nodes that are too small, fully reserved, non-overlapping high, or split-all-reserved; successful reservations confined to the requested node; correct full merges at node borders; and shared range tests passing with `memblock_alloc_exact_nid_raw`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.h

## Purpose

`alloc_exact_nid_api.h` declares entrypoints for exact-NID memblock allocation tests and gates NUMA-specific checks on `CONFIG_NUMA`.

## Important APIs, Types, and Functions

It declares `memblock_alloc_exact_nid_checks()` and `__memblock_alloc_exact_nid_numa_checks()`. Inline `memblock_alloc_exact_nid_numa_checks()` calls the implementation and returns zero when `CONFIG_NUMA` is enabled; otherwise it is a no-op returning zero.

## Control Flow

The header-level control flow is compile-time conditional. Non-NUMA builds still compile and run the top-level exact-NID suite without trying to execute NUMA-only checks.

## State and Persistence Behavior

The header stores no state. It controls whether NUMA test state is exercised by the implementation.

## Dependencies and Integration Points

It includes `common.h` and is used by `alloc_exact_nid_api.c` and `main.c`. It also connects to `alloc_nid_api.c` through shared range checks.

## Risks and Edge Cases

The inline wrapper discards the return value from `__memblock_alloc_exact_nid_numa_checks()`, so failures must abort through assertions rather than return codes. Non-NUMA builds provide no coverage for strict exact-node semantics.

## Test Signals

Builds with and without `CONFIG_NUMA` should compile. NUMA-enabled runs should print and execute exact-NID NUMA scenarios; non-NUMA runs should skip them cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_exact_nid_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.c

## Purpose

`alloc_helpers_api.c` tests the helper API `memblock_alloc_from()`, which allocates memory above a minimum address while still prioritizing successful allocation when the minimum cannot be satisfied.

## Important APIs, Types, and Functions

Scenarios cover simple aligned minimum address allocation, misaligned minimum rounding, high minimum addresses too close to the end of memory, no space above the minimum, and minimum addresses below the start of available memory. Direction-specific functions model top-down and bottom-up placement. `memblock_alloc_helpers_checks()` runs all helper scenarios.

## Control Flow

The suite initializes dummy physical memory, resets memblock attributes, and runs wrappers that execute both allocation directions. Each scenario calls `setup_memblock()`, optionally reserves blocking regions, invokes `memblock_alloc_from(size, align, min_addr)`, and asserts reserved-region base, size, count, total size, and zeroed memory where applicable.

## State and Persistence Behavior

It manipulates global memblock allocation direction and reservation arrays. Dummy physical memory is initialized once for the suite and cleaned afterward. The helper API is expected to return zeroed memory, not raw contents.

## Dependencies and Integration Points

It depends on `alloc_helpers_api.h`, `common.h`, and real memblock helper behavior. `main.c` invokes `memblock_alloc_helpers_checks()` after generic allocation tests.

## Risks and Edge Cases

The key risk is policy ambiguity: several tests expect allocation to succeed below `min_addr` if no suitable memory exists above it. Changes that make `min_addr` strict would intentionally break these assertions. Misalignment and start/end capping are sensitive to `SMP_CACHE_BYTES`.

## Test Signals

Passing signals include aligned placement at or above `min_addr` when possible, fallback allocation when the minimum is impossible, correct merging with adjacent reservations, zeroed allocation contents, and accurate reservation counters in both allocation directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.h

## Purpose

`alloc_helpers_api.h` declares the memblock helper allocation test entrypoint.

## Important APIs, Types, and Functions

It includes `common.h` and declares `int memblock_alloc_helpers_checks(void);`.

## Control Flow

There is no control flow in the header. The simulator entrypoint calls the declared function.

## State and Persistence Behavior

The header contains no state.

## Dependencies and Integration Points

It integrates `alloc_helpers_api.c` with `main.c` and shared memblock test helpers.

## Risks and Edge Cases

Only one top-level function is exposed, so selective helper test execution is not available through this header.

## Test Signals

Successful compilation and linkage confirm the declaration matches the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_helpers_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.c -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.c

## Purpose

`alloc_nid_api.c` tests range-limited and NUMA-aware memblock allocation through `memblock_alloc_try_nid()`, `memblock_alloc_try_nid_raw()`, and, for shared range cases, `memblock_alloc_exact_nid_raw()`. It verifies alignment, range clipping, reservation merging, fallback behavior, node selection, and memory zeroing/raw semantics.

## Important APIs, Types, and Functions

`get_memblock_alloc_nid_name()` labels the active API. `run_memblock_alloc_nid()` dispatches based on `TEST_F_RAW` and `TEST_F_EXACT`. Range tests cover simple ranges, misaligned start/end, exact-address fit, narrow ranges, low max failure, min/max-adjacent reserved merges, reserved gaps with and without space, full merge, all reserved, and min/max capping. NUMA tests use `node_fractions` to cover requested-node success, small-node fallback, fully reserved node fallback, partial reservation success and fallback, split ranges, no-overlap ranges, large-region failure, reserved full merge, split-all-reserved failure, and `memblock_alloc_node()` nid tagging.

## Control Flow

The suite first runs range checks with `NUMA_NO_NODE`, then NUMA checks through `memblock_alloc_nid_numa_checks()`. Direction wrappers set top-down or bottom-up mode, because placement differs by direction while final reservations must still satisfy range and node policy. `memblock_alloc_nid_checks()` runs both zeroing and raw try-NID modes; `memblock_alloc_exact_nid_range_checks()` reuses range checks with exact/raw dispatch.

## State and Persistence Behavior

State includes `alloc_nid_test_flags`, global memblock arrays, per-region `nid` metadata, allocation direction, and dummy physical memory. Normal try-NID allocations are expected to zero memory, while raw and exact raw allocations are expected to leave nonzero dummy contents. Each top-level run resets attributes and initializes/cleans dummy memory.

## Dependencies and Integration Points

It includes `alloc_nid_api.h` and common helpers, and it is used both directly by `main.c` and indirectly by `alloc_exact_nid_api.c` for shared range tests. It depends on NUMA setup helpers and the real memblock allocator implementation.

## Risks and Edge Cases

Fallback rules are subtle: try-NID may fall back to `NUMA_NO_NODE`, while exact-NID must not. Range bounds can be dropped or capped in some cases, and tests assert those policies precisely. The file is large and scenario-rich, so adding allocator behavior without updating mirrored top-down/bottom-up cases can leave asymmetric coverage.

## Test Signals

Passing signals include correct reserved table geometry for every range case, fallback to suitable nodes for try-NID, no allocation for truly impossible ranges, correct `nid` on `memblock_alloc_node()`, zeroed versus raw memory content, and successful reuse of range checks by exact-NID mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.h

## Purpose

`alloc_nid_api.h` declares the range and NUMA memblock allocation test entrypoints and provides compile-time gating for NUMA-specific checks.

## Important APIs, Types, and Functions

It declares `memblock_alloc_nid_checks()`, `memblock_alloc_exact_nid_range_checks()`, and `__memblock_alloc_nid_numa_checks()`. Inline `memblock_alloc_nid_numa_checks()` calls the NUMA implementation only when `CONFIG_NUMA` is enabled; otherwise it returns zero.

## Control Flow

Compile-time `#ifdef CONFIG_NUMA` controls whether NUMA scenarios run. Range tests remain available regardless of NUMA support.

## State and Persistence Behavior

The header stores no state. The implementation manages allocator flags, memblock arrays, and dummy memory.

## Dependencies and Integration Points

It includes `common.h`, is consumed by `alloc_nid_api.c`, `alloc_exact_nid_api.c`, and `main.c`, and exposes the shared exact-NID range check hook.

## Risks and Edge Cases

As with the exact-NID header, the inline NUMA wrapper ignores the implementation return value and relies on assertions for failure. Non-NUMA builds do not cover fallback and node-tagging behavior.

## Test Signals

Both NUMA and non-NUMA builds should compile. NUMA builds should run the additional try-NID scenarios; exact-NID tests should link against `memblock_alloc_exact_nid_range_checks()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/tests/alloc_nid_api.h -->
