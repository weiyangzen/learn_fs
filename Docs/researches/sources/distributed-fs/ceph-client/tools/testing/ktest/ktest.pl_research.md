# sources/distributed-fs/ceph-client/tools/testing/ktest/ktest.pl

## Purpose

`ktest.pl` is a Perl automation harness for building Linux kernels, installing them on a target, rebooting or power cycling the target, monitoring a serial console, running target-side tests, and orchestrating higher-level workflows such as git bisect, config bisect, patch checking, minimum-config discovery, and warnings-file generation. It is heavily driven by a custom config-file language documented in `sample.conf` and exercised by the example configs in this group.

## Important APIs, Types, And Data

The primary public interface is the config option set stored in `%opt` and mapped into lexical globals by `%option_map`. Defaults include mail behavior, `NUM_TESTS`, `TEST_TYPE`, `BUILD_TYPE`, `MAKE_CMD`, timeouts, reboot/power policies, SSH/SCP command templates, bootloader settings, and logging. Config parsing supports `TEST_START`, `DEFAULTS`, `SKIP`, `ITERATE`, `OVERRIDE`, `IF`/`ELSE IF`/`ELSE`, `INCLUDE`, option assignment with `=`, config variables with `:=`, and regex transformations with `=~`.

Important routines include `read_config()`/`__read_config()` for parsing, `process_variables()` and `eval_option()` for variable and per-test option expansion, `run_command()`/`run_ssh()`/`run_scp_*()` for shell execution, `open_console()`/`wait_for_monitor()`/`monitor()` for target console monitoring, `build()`/`install()`/`make_oldconfig()` for kernel build/install, `do_run_test()` for target test execution, `bisect()`, `config_bisect()`, `patchcheck()`, `make_min_config()`, `make_warnings_file()`, and mail/log helpers.

## Control Flow

Startup parses `-D` overrides, `--dry-run`, and an optional config path. If the config does not exist, ktest interactively generates a starter file. `read_config()` recursively parses includes, command-line overrides, mandatory-option prompts, defaults, and unused-option checks. In dry-run mode it prints resolved options and exits.

Normal execution opens the log, prints the preamble, and iterates from test 1 through `NUM_TESTS`. For each test, it resolves per-test/default/repeated options, changes to `BUILD_DIR`, creates `OUTPUT_DIR` and `TMP_DIR`, configures environment variables, runs first-test `PRE_KTEST`, per-test `PRE_TEST`, optional checkout and add-config composition, and dispatches by `TEST_TYPE`. Special test types (`bisect`, `config_bisect`, `patchcheck`, `make_min_config`, `make_warnings_file`) enter dedicated workflows. Ordinary tests build unless `BUILD_TYPE=nobuild`, optionally install, boot/monitor, run a target test command, print timing, and call `success()` or `fail()`.

## State And Persistence Behavior

The script mutates a large amount of state: output `.config`, `localversion`, build logs, test logs, dmesg logs, optional global `LOG_FILE`, temporary files under `TMP_DIR`, failure/success archives, target kernel images and modules, target initrd via post-install hooks, bootloader one-shot entries, git checkout/bisect state, warnings baseline files, min-config output/ignore files, and email notifications. It stores derived state in globals across the current test iteration and deliberately resets some values such as timing, `%force_config`, and `$have_version` per iteration.

## Dependencies And Integration Points

The script depends on Perl core modules `IPC::Open2`, `Fcntl`, `File::Path`, `File::Copy`, `FileHandle`, `FindBin`, and `IO::Handle`; on shell commands such as `make`, `git`, `ssh`, `scp`, `tar`, `diffstat`, bootloader tools, power scripts, and mailers; and on target console access. It integrates with Linux Kconfig/build systems, grub/grub2/grub2 BLS/syslinux/script reboot methods, `config-bisect.pl`, `scripts/diffconfig`, external target tests, and the example/sample config language.

## Risks And Edge Cases

The script intentionally executes arbitrary shell from config files, so config trust is required. Many commands are destructive: `make mrproper`, git checkout/reset hooks, target module removal, power cycling, kernel installation, and bootloader one-shot changes. Global mutable state makes behavior sensitive to per-test option resolution and repeated tests. Console handling changes terminal settings and must restore them on failures. Warning parsing is text-based and compiler/path sensitive. Config parsing catches duplicate options but allows complex variable expansion and shell substitution that can surprise users. There is an apparent typo in `do_run_test()` where `BISECT_RET_BAD` compares `$child_exit` to `$bisect_ret_skip` instead of `$bisect_ret_bad`, making custom bad return-code handling suspect.

## Test Signals

Low-risk validation starts with `ktest.pl --dry-run` for representative configs and `-D` overrides. Runtime smoke tests should cover build-only, boot-only, and test workflows with a disposable target. Specific regression checks should cover include parsing, `IF`/`ELSE`, `ITERATE`, `DEFAULTS OVERRIDE`, option recursion limits, warning-file comparison, reboot-type selection, bisect skip/replay/check flows, patchcheck commit ordering, and `make_min_config` resume behavior. Logs to inspect are the main log, buildlog, dmesg, testlog, git bisect log, warnings file, and saved failure/success directories.
