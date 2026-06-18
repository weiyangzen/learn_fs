# sources/distributed-fs/ceph-client/tools/testing/selftests/nolibc/run-tests.sh

Purpose: shell runner for building and running nolibc tests over many target architectures with prebuilt kernel.org nolibc cross toolchains.

Important APIs/functions: option parsing uses `getopt`; `crosstool_arch()` and `crosstool_abi()` translate selftest architecture names to toolchain triples; `download_crosstool()` fetches and extracts `${hostarch}-gcc-${version}-nolibc-${arch}-${abi}.tar.gz`; `swallow_output()` hides successful make output; `test_arch()` configures, builds, runs, and reports one architecture.

Control flow: defaults include GCC 15.2.0, host `x86_64`, cache-backed download/build directories, `system` mode, and all supported arch names. Options select jobs, download permission, cache paths, crosstool version, host arch, build directory, user/system mode, Werror, LLVM, and target arch list. If `-p` is set it downloads all selected toolchains before running. For each arch it checks toolchain presence, constructs a `make -f Makefile.nolibc` invocation with `XARCH`, `CROSS_COMPILE`, optional `LLVM`, and per-arch `O=`, then runs `defconfig` and either `run` or `run-user`.

State and persistence: downloads and extracts toolchains under `${XDG_CACHE_HOME:-$HOME/.cache}/crosstools/`, writes per-arch build trees under `nolibc-tests`, copies `run.out` to `run.out.$arch`, and leaves build artifacts for reuse. It does not edit source files.

Dependencies/integration: requires `curl`, `tar`, GNU `make`, `realpath`, kernel selftest `Makefile.nolibc`, and cross toolchains. It integrates with `nolibc-test.c` as the test payload and with QEMU/user-mode targets provided by nolibc make rules.

Risks: the script uses `set -e`, so an unsupported or failing architecture stops the entire run except for explicit unsupported LLVM/user combinations. Download URLs are fixed to kernel.org layout. `CFLAGS_EXTRA` is appended within `test_arch()` and can accumulate if exported externally. Some arch/mode combinations are skipped by printed message rather than kselftest TAP.

Test signals: per-arch output starts with a left-aligned `arch:` label; unsupported configurations print that status; successful make report output is filtered through `grep passed`; failures dump captured build/run output through `swallow_output()`.
