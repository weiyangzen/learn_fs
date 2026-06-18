# sources/distributed-fs/ceph-client/scripts/dummy-tools/gcc

Purpose: Dummy compiler shim that makes Kconfig compiler feature probes succeed when preparing broad kernel configurations without a real target toolchain.

Important APIs/functions: Shell function `arg_contain()` tests whether an option is present. Special cases implement `--version`, `-E` preprocessing for GCC version macros, `-Wa,--version`, `-S` probes for stack protector and PowerPC checks, `-print-file-name=plugin`, and inverted failure for `-D__SIZEOF_INT128__=0`.

Control flow: The script checks recognized probe patterns in order and emits minimal expected output or exits with expected status. Most unrecognized invocations fall through to exit status 0 with no output.

State/persistence: Stateless. It reads stdin for preprocessing and emits probe-specific text to stdout/stderr.

Dependencies/integration: Used as `CROSS_COMPILE=scripts/dummy-tools/`, so kernel build checks invoke this as a compiler. Integrates with scripts such as `cc-version.sh`, Kconfig `cc-option`, GCC plugin path probing, assembler version probing, and arch capability scripts.

Risks: It intentionally lies about feature support and must not be used for real compilation. Probe-specific output can become stale as Kbuild checks evolve. `readlink -f` may vary on non-GNU hosts.

Test signals: Run representative Kbuild probes for version, preprocessing macros, assembler version, stack protector, PowerPC profile/patchable entry, plugin path, and int128 negative check.
