# sources/distributed-fs/ceph-client/tools/testing/ktest/sample.conf

## Purpose

`sample.conf` is the user-facing reference document for the `ktest.pl` configuration language and option surface. It is not meant to run unchanged; it explains how to define defaults, tests, includes, variables, mandatory target/build options, email, build/install/reboot/test behavior, patchcheck, bisect, config bisect, min-config, warnings-file generation, and miscellaneous operational flags.

## Important APIs, Types, And Data

The file documents `TEST_START`, `DEFAULTS`, `ITERATE`, `SKIP`, `OVERRIDE`, conditional `IF`/`ELSE`, `INCLUDE`, config variables with `:=`, ktest options with `=`, `${VAR}` expansion, `${shell command}` expansion, and `=~` regex transformations. It lists mandatory/default options such as `MACHINE`, `SSH_USER`, `BUILD_DIR`, `OUTPUT_DIR`, `BUILD_TARGET`, `TARGET_IMAGE`, `POWER_CYCLE`, `CONSOLE`, `LOCALVERSION`, `REBOOT_TYPE`, `GRUB_MENU`, `GRUB_FILE`, `SYSLINUX_LABEL`, and hook options such as `PRE_KTEST`, `POST_KTEST`, `PRE_TEST`, `POST_TEST`, `PRE_BUILD`, `POST_BUILD`, `PRE_INSTALL`, and `POST_INSTALL`.

## Control Flow

The document follows the same conceptual order as `ktest.pl`: parse defaults/test sections and variables, satisfy mandatory options, build or configure the kernel, install as needed, set the bootloader, monitor the console, run tests, and handle special test types. For each special workflow it explains which options ktest later requires: patchcheck commit ranges and warning policy, git bisect good/bad/type/check/replay/return-code policy, config-bisect good/bad configs and external executor, min-config output/start/ignore/test type, and make-warnings-file prerequisites.

## State And Persistence Behavior

The sample describes persistent artifacts created or consumed by ktest: config files, build and output directories, target kernel image and modules, temporary directories, logs, failure archives, warnings baselines, git bisect metadata, config-bisect temp configs, min-config output and ignore files, bootloader state, email payloads, and optional target-side initrd or BLS entries through hooks.

## Dependencies And Integration Points

It is tightly coupled to the option names and semantics in `ktest.pl`'s `%default` and `%option_map`. It also references Linux build targets, bootloaders, SSH/SCP, mailers, git, `diffconfig`, `config-bisect.pl`, target test scripts, power-control infrastructure, syslinux, grub2/grub2bls, and kernel-install/BLS workflows.

## Risks And Edge Cases

Because this is exhaustive documentation, drift from `ktest.pl` is the main risk. Users can copy destructive examples such as power cycling, module deletion, or git resets without adapting them. The distinction between config variables (`:=`, evaluated while parsing) and options (`=`, evaluated per test) is easy to miss. Some workflows rely on long-lived external state, such as existing git bisects or partial min-config outputs, and prompt behavior changes in unattended runs.

## Test Signals

Documentation validation is mostly by cross-checking option names against `ktest.pl`, running `ktest.pl --dry-run` on examples derived from the sample, and ensuring every documented special `TEST_TYPE` still maps to a live implementation. Runtime test signals are the same as the script: resolved-option preambles, build/test logs, console dmesg, warnings files, git/config-bisect logs, and final ktest result banners.
