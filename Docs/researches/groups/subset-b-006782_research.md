# subset-b-006782 grouped research

This grouped report covers Linux `tools/testing/ktest` example/configuration files and Linux `tools/testing/kunit` command, configuration, execution, JSON, and KTAP parsing helpers in the Ceph client source copy. Each section is source-tree aligned for reconciliation into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bisect.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bisect.conf

## Purpose

This ktest include defines reusable test sections for two bisect-oriented workflows: a normal git bisect driven by ktest build/boot/test results, and a config bisect driven by a known bad `.config` versus a good or minimum config. It is meant to be included by machine-specific files such as `test.conf`, `kvm.conf`, or `vmware.conf` after they set `TEST`, machine access, and default paths.

## Important APIs, Types, And Data

The effective API is the ktest config language consumed by `ktest.pl`: `DEFAULTS IF`, `TEST_START IF`, immediate variables assigned with `:=`, and per-test options assigned with `=`. `RUN_TEST` is a reusable variable defaulting to `${SSH} hackbench 50`. The `TEST == bisect` section sets `TEST_TYPE=bisect`, `BISECT_GOOD`, `BISECT_BAD`, `CHECKOUT`, `BISECT_TYPE=test`, `TEST=${RUN_TEST}`, `BISECT_CHECK=1`, and `MIN_CONFIG=${THIS_DIR}/config-bisect`. The `TEST == config-bisect` section sets `TEST_TYPE=config_bisect`, `CONFIG_BISECT_TYPE=boot`, `CONFIG_BISECT`, and `CONFIG_BISECT_GOOD`.

## Control Flow

`ktest.pl` reads the including file, expands `INCLUDE include/bisect.conf`, evaluates the `DEFAULTS` block if `RUN_TEST` was not already defined, and materializes only the `TEST_START` block whose condition matches the caller's `${TEST}` variable. For a git bisect, execution later flows through `bisect()`, optional good/bad verification, repeated `run_bisect()` build/boot/test attempts, and `git bisect good|bad|skip`. For config bisect, execution flows through `config_bisect()`, oldconfig normalization of good and bad configs, then repeated invocations of `config-bisect.pl`.

## State And Persistence Behavior

The file itself is static. It points ktest at persistent git state in `BUILD_DIR`, a persistent bisect minimum config at `${THIS_DIR}/config-bisect`, bad/good config files under `${THIS_DIR}`, and optional replay state if `BISECT_REPLAY` or `BISECT_START` is uncommented. Runtime state is stored by `ktest.pl` in git bisect metadata, logs, temporary configs, dmesg/test/build logs, and possibly failure directories configured elsewhere.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${SSH}`, `${THIS_DIR}`, `${CONFIG_DIR}`, machine, build, log, and reboot defaults. It integrates with `ktest.pl` options for `bisect`, `config_bisect`, `BISECT_RET_*`, `BISECT_SKIP`, `BISECT_MANUAL`, `CONFIG_BISECT_EXEC`, and target test execution. The default `RUN_TEST` assumes `hackbench` is available on the target over SSH.

## Risks And Edge Cases

The sample commits (`v3.3`, `HEAD`, `origin/master`) are placeholders and can bisect the wrong range if copied unchanged. `BISECT_CHECK=1` is safer but expensive and can mutate hardware state before the real search. `BISECT_SKIP` defaults are nuanced: build/boot failures during test bisects may be skipped unless disabled. Config bisect assumes the bad config is generally a superset of the good config; missing required configs or dependency-selected options can produce inconclusive results.

## Test Signals

Useful validation is `ktest.pl --dry-run <machine.conf>` with `TEST:=bisect` and `TEST:=config-bisect` overrides, checking that exactly the intended `TEST_TYPE`, commits, configs, and `TEST` command resolve. Runtime evidence includes git bisect progress, generated `good_config`/`bad_config` files for config bisect, build/test logs, and final ktest result banners.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bisect.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bootconfig.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bootconfig.conf

## Purpose

This include defines ktest test cases that install bootconfig snippets into a target initrd, reboot or reuse a kernel, and run verifier scripts for tracing-related bootconfig scenarios. It is an example for testing bootconfig scripts rather than for building a new kernel each time.

## Important APIs, Types, And Data

The file defines immediate variables and ktest options: `INITRD`, `BOOTCONFIG`, `BUILD_TYPE`, `ADD_BOOTCONFIG`, `BOOTCONFIG_TEST_PREP`, `CLEAR_BOOTCONFIG`, `DO_TEST`, and `RUN_BOOTCONFIG`. It declares three `TEST_START IF DEFINED RUN_BOOTCONFIG` sections with `TEST_TYPE=test`, distinct `TEST_NAME` values, `BUILD_TYPE=nobuild`, specific `BOOTCONFIG_FILE` and `BOOTCONFIG_VERIFY` values, `ADD_CONFIG=${ADD_CONFIG} ${BOOTCONFIG_PATH}/config-bootconfig`, `PRE_TEST`, `PRE_TEST_DIE=1`, `TEST=${DO_TEST}`, and `POST_TEST=${CLEAR_BOOTCONFIG}`.

## Control Flow

When included, `ktest.pl` creates three test cases if `RUN_BOOTCONFIG` is defined. Each test runs `PRE_TEST` to copy the selected `.bconf` file to the target and use the target `bootconfig` tool to replace/apply it to `${INITRD}`. The test body copies and runs the matching verifier script on the target. `POST_TEST` removes bootconfig data from the initrd after the test.

## State And Persistence Behavior

The runtime state is on the target host: `/tmp/${BOOTCONFIG_FILE}`, `/tmp/${BOOTCONFIG_VERIFY}`, and modifications to `${INITRD}`. `POST_TEST` attempts to clear those bootconfig modifications, but temporary files on the target may remain. ktest logs record prep/test/post-test command output.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${SSH}`, `${SSH_USER}`, and `${MACHINE}`; on an including config for `BOOTCONFIG_PATH`; on `scp`/SSH access; on a target-side bootconfig executable at `${BOOTCONFIG}`; on verifier shell scripts; and on ktest's `PRE_TEST`, `TEST`, and `POST_TEST` hooks. `ADD_CONFIG` integrates with kernel configuration when a build is enabled, but each declared test overrides to `nobuild`.

## Risks And Edge Cases

Because it modifies a real initrd on the target, failed `POST_TEST` cleanup can leave subsequent boots with stale bootconfig settings. `BUILD_TYPE=nobuild` assumes the target kernel/initrd already support bootconfig and tracing. `PRE_TEST_DIE=1` prevents running verifiers after failed preparation, but not all cleanup paths are guaranteed if a critical failure occurs outside normal post-test handling. Missing `BOOTCONFIG_PATH` or verifier files will fail only at runtime/dry-run resolution.

## Test Signals

Dry-run output should show three named bootconfig tests with `nobuild`, `PRE_TEST`, `TEST`, and `POST_TEST` resolved. Runtime success is the verifier exit status plus logs showing bootconfig deletion/addition before testing and deletion afterward. Manual validation can inspect the initrd with `${BOOTCONFIG} -l` or equivalent before and after a run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/bootconfig.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/defaults.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/defaults.conf

## Purpose

This include provides shared defaults for machine-specific ktest examples. It centralizes directory layout, SSH access, kernel build/install paths, reboot/power handling, logging, minimum config locations, and success-line defaults so individual machine configs can focus on target-specific console and test selection.

## Important APIs, Types, And Data

The file uses ktest `DEFAULTS IF NOT DEFINED`, unconditional `DEFAULTS`, and `DEFAULTS ELSE IF` blocks. Important variables/options include `BOX`, `BITS`, `THIS_DIR`, `CONFIG_DIR`, `CLEAR_LOG`, `SSH_USER`, `SSH`, `TEST`, `BUILD_DIR`, `OUTPUT_DIR`, `BUILD_TARGET`, `TARGET_IMAGE`, `SCRIPTS_DIR`, `POWER_CYCLE`, `POWER_OFF`, `LOCALVERSION`, `GRUB_MENU`, `BUILD_OPTIONS`, `LOG_FILE`, `MIN_CONFIG`, optional `ADD_CONFIG`, and `REBOOT_SUCCESS_LINE`. The `REBOOT` variable drives one of four policy branches: `none`, `error`, `fail`, or default.

## Control Flow

During config parsing, `ktest.pl` first defaults `BOX` to `${MACHINE}` and `BITS` to `64` if the including config did not set them. The main `DEFAULTS` block then sets common options. Conditional `DEFAULTS` branches translate the caller's `${REBOOT}` variable into `REBOOT_ON_SUCCESS`, `REBOOT_ON_ERROR`, `POWEROFF_ON_ERROR`, `POWEROFF_ON_SUCCESS`, `POWEROFF_AFTER_HALT`, `DIE_ON_FAILURE`, and `STORE_FAILURES`.

## State And Persistence Behavior

The include defines persistent output locations but does not write them itself. `ktest.pl` will create `${OUTPUT_DIR}`, write `${LOG_FILE}`, use `${CONFIG_DIR}/config-min`, and potentially write `${THIS_DIR}/failures` when failures occur. Power scripts under `${SCRIPTS_DIR}` and target bootloader entries are external persistent infrastructure.

## Dependencies And Integration Points

It depends on an including config setting at least `MACHINE` and a console, and on ktest's option map for all named options. It integrates with later includes (`patchcheck.conf`, `tests.conf`, `bisect.conf`, `min-config.conf`, `bootconfig.conf`) by defining common variables they reuse. It assumes x86 defaults for `BUILD_TARGET`, `TARGET_IMAGE`, and `GRUB_MENU`, while documenting that other architectures can override.

## Risks And Edge Cases

The default SSH user is `root` and assumes passwordless access, which is powerful and risky. `BUILD_DIR` and `OUTPUT_DIR` are under `${THIS_DIR}` and must not alias each other. The default `POWER_CYCLE`/`POWER_OFF` script names must exist for hardware tests. `REBOOT := empty` in examples falls into the default branch, enabling reboot on success and error. The `fail` policy disables `DIE_ON_FAILURE`, so failures may be logged while the run continues.

## Test Signals

`ktest.pl --dry-run` should resolve machine-specific `CONFIG_DIR`, `OUTPUT_DIR`, `LOG_FILE`, `MIN_CONFIG`, power commands, and reboot policy. Runtime validation includes log creation, build output under `${THIS_DIR}/build/${MACHINE}`, and correct reboot/power behavior for each `REBOOT` policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/defaults.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/min-config.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/min-config.conf

## Purpose

This include defines example `make_min_config` workflows for deriving a small bootable or test-capable kernel config for a target. It is intended for long-running ktest sessions that repeatedly remove candidate config options and verify whether the machine still boots or can run a simple SSH test.

## Important APIs, Types, And Data

The file exposes two conditional test sections. When `${TEST} == min-config`, it sets `TEST_TYPE=make_min_config`, `OUTPUT_MIN_CONFIG=${CONFIG_DIR}/config-new-min-net`, `IGNORE_CONFIG=${CONFIG_DIR}/config-skip-net`, `MIN_CONFIG_TYPE=test`, `TEST=${SSH} echo hi`, and `USE_OUTPUT_MIN_CONFIG=1`. When `${TEST} == min-config && ${MULTI}`, it creates a second `make_min_config` test writing `${CONFIG_DIR}/config-new-min`, using `${CONFIG_DIR}/config-skip`, and starting from `${CONFIG_DIR}/config-new-min-net`.

## Control Flow

`ktest.pl` parses the include and adds one or two tests depending on `TEST` and `MULTI`. Execution later flows through `make_min_config()`: build `allnoconfig`, read Kconfig dependencies, compare the starting minimum config against ignored/default configs, disable one candidate at a time, build and boot/test, then either keep the option in `IGNORE_CONFIG` or remove it from the output minimum config.

## State And Persistence Behavior

This include intentionally creates and updates persistent config files under `${CONFIG_DIR}`. `OUTPUT_MIN_CONFIG` is a resumable product; `IGNORE_CONFIG` records configs found to be required. With `USE_OUTPUT_MIN_CONFIG=1`, reruns automatically continue from existing output instead of prompting. The second test depends on the first test's network-capable output file.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${CONFIG_DIR}` and `${SSH}`. It uses `ktest.pl` support for `TEST_TYPE=make_min_config`, `OUTPUT_MIN_CONFIG`, `IGNORE_CONFIG`, `MIN_CONFIG_TYPE`, `START_MIN_CONFIG`, and `USE_OUTPUT_MIN_CONFIG`. The test-capable first pass requires SSH access after boot; the boot-only second pass only requires console boot detection.

## Risks And Edge Cases

Runs can take many hours or days and involve repeated target reboots. Interruptions are expected, but corrupted or stale `OUTPUT_MIN_CONFIG`/`IGNORE_CONFIG` files can bias future runs. Dependency inference from Kconfig is heuristic and cannot perfectly handle all `select`/default interactions. The second pass assumes `${CONFIG_DIR}/config-new-min-net` exists or is produced by the first pass.

## Test Signals

Dry-run output should show one `make_min_config` test when `MULTI=0` and two when `MULTI=1`. Runtime signals include periodic updates to `config-new-min-net`, `config-skip-net`, `config-new-min`, and `config-skip`, plus ktest logs showing candidate configs being disabled or kept.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/min-config.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/patchcheck.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/patchcheck.conf

## Purpose

This include defines an example patch-by-patch validation workflow for a git commit range. It can build, boot, or test every commit from `PATCH_START` through `PATCH_END`, and optionally generate a baseline warnings file before the patchcheck run.

## Important APIs, Types, And Data

Important variables include `PATCH_START`, `PATCH_END`, `DO_BUILD_TYPE`, `PATCH_CHECKOUT`, `PATCH_CONFIG`, `PATCH_TEST`, `PATCH_TEST_TYPE`, `WARNINGS_FILE`, and `PATCH_START1`. Conditional sections set `TEST_TYPE=make_warnings_file` when `CREATE_WARNINGS_FILE` is defined, and one or two `TEST_TYPE=patchcheck` sections when `${TEST} == patchcheck`, with the multi variant changing `MAKE_CMD` to `CC=gcc-4.5.1 make`.

## Control Flow

The include first normalizes `DO_BUILD_TYPE` from an already-defined `BUILD_TYPE` or defaults to `oldconfig`. If `PATCH_TEST` is defined, patchcheck type is `test`; otherwise it is `boot`. If `CREATE_WARNINGS_FILE` is defined, an initial `make_warnings_file` test checks out `${PATCHCHECK_START}~1`, forces a full build, and writes `${OUTPUT_DIR}/warnings_file`. Patchcheck tests then call `ktest.pl`'s `patchcheck()` routine, which enumerates commits, checks each out, builds with `${PATCH_CONFIG}`, checks warnings, then optionally boots and runs `${PATCH_TEST}`.

## State And Persistence Behavior

The git worktree in `BUILD_DIR` is moved across commits and branch checkout. `${PATCH_CONFIG}` is read as the fixed min config. `${OUTPUT_DIR}/warnings_file` may be generated and later consumed to distinguish old from new warnings. ktest writes build logs, dmesg, test logs, and normal result logs.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${CONFIG_DIR}`, `${OUTPUT_DIR}`, and `${SSH}`; on a git worktree; on `diffstat` and `git show` behavior in `ktest.pl`; on a valid branch in `PATCH_CHECKOUT`; and on target-side `/usr/local/bin/ktest-test-script` if using the default `PATCH_TEST`. It integrates with `WARNINGS_FILE`, `IGNORE_WARNINGS`, `PATCHCHECK_SKIP`, and `PATCHCHECK_CHERRY` support documented in `sample.conf`.

## Risks And Edge Cases

The example uses placeholder commits (`HEAD~3` to `HEAD`) and branch `test/branch`. There is a naming mismatch in the warnings-file pre-test: `CHECKOUT = ${PATCHCHECK_START}~1` is set in a section that otherwise defines `PATCH_START`, so users must ensure the variable they intend is available. Incremental builds can hide clean-build failures except on first and last patches unless `BUILD_NOCLEAN` is controlled. Warning matching is textual and can be affected by compiler version and path formatting.

## Test Signals

Dry-run should show the selected `PATCHCHECK_START`, `PATCHCHECK_END`, `PATCHCHECK_TYPE`, `CHECKOUT`, `MIN_CONFIG`, and optional warnings-file generation. Runtime validation includes the printed commit list, per-commit checkout/build logs, warning comparisons, boot/test results, and a final success banner only after all unskipped commits pass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/patchcheck.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/tests.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/tests.conf

## Purpose

This include provides common build, boot, test, and randconfig test definitions selected by a caller's `${TEST}` variable. It lets multiple machine configs share the same test matrix while overriding the machine-specific defaults elsewhere.

## Important APIs, Types, And Data

It uses immediate variables `BOOT_TYPE` and `RUN_TEST`, both defaulted when not already defined. The file declares conditional `TEST_START` blocks for `TEST == boot`, `build`, `randconfig`, `randconfig && MULTI`, and `test`. Key options are `TEST_TYPE`, `BUILD_TYPE=${BOOT_TYPE}` or `randconfig`, `BUILD_NOCLEAN=1`, `MIN_CONFIG`, `MAKE_CMD`, and `TEST=${RUN_TEST}`.

## Control Flow

`ktest.pl` includes the file after machine defaults are set. Exactly one or more sections are included depending on the config-time `${TEST}` and `${MULTI}` variables. Build and boot tests run a single kernel build path; randconfig creates ten iterations through `TEST_START ITERATE 10`; the multi randconfig adds a boot-only variant using a smaller min config and default `make`.

## State And Persistence Behavior

The include does not write state directly. It controls ktest state through generated test cases and repeated iteration counters. Randconfig tests create changing `.config` files and build artifacts in the configured output directory. `BUILD_NOCLEAN=1` preserves build products across many normal build/boot/test cases.

## Dependencies And Integration Points

It depends on `include/defaults.conf` for `${CONFIG_DIR}`, `${SSH}`, machine paths, and build options. It integrates with ktest's `build`, `boot`, `test`, and `randconfig` handling. The default `RUN_TEST` assumes `hackbench` is installed and runnable over the configured SSH connection.

## Risks And Edge Cases

`BUILD_NOCLEAN=1` improves speed but can preserve stale generated artifacts. Randconfig tests require an appropriate `MIN_CONFIG`; without a network-capable config, the test variant may fail after boot because SSH never comes up. `${TEST}` is a config variable, while `TEST = ...` is a runtime command option; confusing the two can select the wrong workflow or command.

## Test Signals

Dry-run should show the intended `TEST_TYPE`, `BUILD_TYPE`, and repeated randconfig count. Runtime signals include successful build-only result banners, monitor logs reaching the configured success line for boot tests, and target command exit status for `TEST_TYPE=test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/include/tests.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/kvm.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/kvm.conf

## Purpose

This is a machine-specific example for running ktest against a libvirt/KVM guest named `Guest`. It demonstrates how to reuse the generic include files while replacing physical power control and serial console handling with `virsh` commands.

## Important APIs, Types, And Data

The config sets `MACHINE=Guest`, `CONSOLE=virsh console ${MACHINE}`, `CLOSE_CONSOLE_SIGNAL=KILL`, `TEST:=patchcheck`, `MULTI:=0`, `BITS:=64`, and `REBOOT:=empty`. It includes `include/defaults.conf`, sets `POST_INSTALL` to run `dracut` on the guest, defines `POWERCYCLE_AFTER_REBOOT=3` and `POWEROFF_AFTER_HALT=20`, then uses `DEFAULTS OVERRIDE` to replace `POWER_CYCLE` with `virsh destroy/start`. It includes patchcheck, tests, bisect, min-config, and bootconfig test definitions.

## Control Flow

`ktest.pl` reads the top-level machine settings, imports defaults, then overrides `POWER_CYCLE` after defaults have already defined it. Later includes materialize test sections according to `TEST` and `MULTI`, which by default means patchcheck. At runtime, console monitoring is through a child process running `virsh console`; reboot failures trigger a delayed `virsh destroy`/`virsh start` power cycle.

## State And Persistence Behavior

Persistent state exists in the guest disk and host libvirt domain. Kernel images/modules/initramfs are installed inside the guest via SSH/SCP and `dracut`; libvirt domain state is mutated by destroy/start operations. ktest writes logs and build outputs under paths inherited from defaults.

## Dependencies And Integration Points

It depends on libvirt `virsh`, a guest named `Guest`, passwordless root SSH, a Fedora-like guest with `/sbin/dracut`, a working serial console, and the generic include files. It integrates with ktest's `CONSOLE`, `CLOSE_CONSOLE_SIGNAL`, `POWER_CYCLE`, `POST_INSTALL`, and reboot fallback options.

## Risks And Edge Cases

`virsh destroy` is abrupt and can corrupt guest state if filesystems are not stable. Killing `virsh console` with `KILL` avoids stuck console sessions but prevents graceful cleanup. `POST_INSTALL` assumes the target image path and initramfs name match the guest bootloader. `REBOOT:=empty` falls into the default reboot-on-success/error policy from defaults.

## Test Signals

Dry-run should resolve `POWER_CYCLE` to the virsh destroy/start sequence and show patchcheck as the default test. Runtime validation includes seeing serial console output through `virsh console`, successful `dracut` post-install commands, and correct forced power cycles after reboot stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/kvm.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/snowball.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/snowball.conf

## Purpose

This is an embedded ARM board example originally used for a Snowball board. It demonstrates non-x86 ktest usage with a cross-compile toolchain, TFTP-style image switching, script-based reboot, and a `make_min_config` workflow.

## Important APIs, Types, And Data

The config defines `THIS_DIR`, `LOG_FILE`, `MAKE_CMD` with ARM `CROSS_COMPILE` and `ARCH=arm`, `ADD_CONFIG`, `SCP_TO_TARGET` as a no-op echo, TFTP paths, `SWITCH_TO_GOOD`, `SWITCH_TO_TEST`, a skipped boot test, an active `TEST_TYPE=make_min_config` test, and a `DEFAULTS` block with `LOCALVERSION`, `POWER_CYCLE`, `CONSOLE`, `REBOOT_TYPE=script`, `SSH_USER`, `BUILD_OPTIONS=-j8 uImage`, `BUILD_DIR`, `OUTPUT_DIR`, `MACHINE`, `TARGET_IMAGE`, and `BUILD_TARGET=arch/arm/boot/uImage`.

## Control Flow

`ktest.pl` parses the skipped boot test but does not materialize it. The active test runs `make_min_config`, starting from `${THIS_DIR}/config.orig`, writing `${THIS_DIR}/config.newmin`, and tracking required configs in `${THIS_DIR}/config.ignore`. For booting, ktest uses `SWITCH_TO_TEST`/`SWITCH_TO_GOOD` copy commands instead of SCP, and `REBOOT_TYPE=script` leaves reboot behavior to configured script hooks.

## State And Persistence Behavior

Persistent state includes the Snowball build directory, TFTP boot images, generated minimum config files, and the ignored-required-config file. Because `SCP_TO_TARGET` is disabled, installation state is managed by copying build outputs to TFTP paths rather than transferring to the target filesystem.

## Dependencies And Integration Points

It depends on an ARM cross compiler under `/usr/local/gcc-4.5.2-nolibc/...`, TFTP paths under `/var/lib/tftpboot`, a console capture source `${THIS_DIR}/snowball-cat`, and ktest's script reboot/image switching hooks. It integrates with `make_min_config`, `ADD_CONFIG`, `BUILD_OPTIONS`, `BUILD_TARGET`, and `TARGET_IMAGE`.

## Risks And Edge Cases

Many paths are highly local to the original environment. `POWER_CYCLE` is an interactive placeholder, so unattended runs will pause. `SCP_TO_TARGET=echo` is intentional for TFTP but would silently skip normal target copies if copied to a different setup. The skipped boot test can be re-enabled accidentally by removing `SKIP` without completing power/reboot scripts.

## Test Signals

Dry-run should show one active `make_min_config` test, ARM make command, script reboot type, and TFTP target image paths. Runtime signals include creation of `config.newmin`/`config.ignore`, `uImage` builds in the Snowball output directory, and image copy commands to the TFTP boot path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/snowball.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/test.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/test.conf

## Purpose

This is the generic physical-machine ktest example. It shows the minimum top-level structure for naming a target, defining a serial console, selecting a shared test workflow, including defaults, and layering common test include files.

## Important APIs, Types, And Data

The config sets `MACHINE=foo`, optional `BOX`, `CONSOLE=stty -F /dev/ttyS0 115200 parodd; cat /dev/ttyS0`, `TEST:=patchcheck`, `MULTI:=0`, `BITS:=64`, `REBOOT:=empty`, and includes `include/defaults.conf`. It also demonstrates optional `PRE_BUILD` and defines `DO_POST_BUILD:=git reset --hard` plus `POST_BUILD=${SSH} 'rm -rf /lib/modules/*-test*'; ${DO_POST_BUILD}` before including patchcheck, tests, bisect, and min-config includes.

## Control Flow

During parsing, defaults establish paths and power/reboot settings from the selected machine. The top-level `TEST` variable controls which included test sections are active; default selection is patchcheck. At runtime, each build can run `POST_BUILD`, removing test modules on the target and resetting the git worktree after a build.

## State And Persistence Behavior

The example mutates both host and target state: build artifacts in `${THIS_DIR}/build/${MACHINE}`, source checkout state through `git reset --hard`, target `/lib/modules/*-test*`, logs, and failure directories from defaults. It does not include `bootconfig.conf`, so bootconfig-specific target initrd state is out of scope.

## Dependencies And Integration Points

It depends on the local serial device `/dev/ttyS0`, root SSH to `${MACHINE}`, power scripts from defaults, a Linux git worktree, and the included ktest fragments. It integrates with `PRE_BUILD`, `POST_BUILD`, `DEFAULTS`, test selection via config variables, and the shared patchcheck/test/bisect/min-config workflows.

## Risks And Edge Cases

`MACHINE=foo` and serial device settings are placeholders. `POST_BUILD` runs `git reset --hard`, which destroys local source changes in `BUILD_DIR`; this is a serious copy/paste risk. The target module cleanup removes all `*-test*` module trees. `REBOOT:=empty` chooses the defaults branch, causing reboots unless users set `none`, `error`, or `fail`.

## Test Signals

Dry-run should show the resolved console command, defaults-derived paths, patchcheck options, and post-build command. Runtime evidence includes serial monitor output, target module cleanup, git reset output, and selected include workflow results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/test.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/vmware.conf -->
# sources/distributed-fs/ceph-client/tools/testing/ktest/examples/vmware.conf

## Purpose

This is a VMware guest example for ktest. It documents serial-pipe setup and configures ktest to monitor the VMware serial socket, install kernels in the guest, and power cycle the VM through `vmrun`.

## Important APIs, Types, And Data

The config sets `MACHINE=Guest`, VMware-specific variables `VMWARE_SERIAL_NAME`, `VMWARE_VM_NAME`, `VMWARE_VM_DIR`, `VMWARE_VM_BASE_DIR`, `CONSOLE=/usr/bin/ncat -U ...`, `VMWARE_HOST_TYPE=ws`, and `VMWARE_POWER_CYCLE=/usr/bin/vmrun -T ... reset ... nogui`. It then mirrors the generic test selection variables, includes defaults, sets `POST_INSTALL` to run `dracut`, configures reboot/halt fallback delays, overrides `POWER_CYCLE=${VMWARE_POWER_CYCLE}`, and includes patchcheck, tests, bisect, and min-config definitions.

## Control Flow

`ktest.pl` parses VMware variables before defaults so later options can reference them. `DEFAULTS OVERRIDE` replaces the generic power script with the VMware reset command. Runtime console monitoring reads the Unix serial pipe with `ncat`; reboot stalls and forced recovery use `vmrun reset`.

## State And Persistence Behavior

Persistent state includes the VM disk, generated initramfs, installed kernel image/modules, VMware VM runtime state, and ktest logs/build outputs. The serial pipe is external state created by VMware configuration. Placeholders such as `<virtual machine name>` must be replaced before use.

## Dependencies And Integration Points

It depends on VMware Workstation/Fusion/Player tooling, `/usr/bin/ncat`, a configured serial port socket, root SSH to the guest, `dracut`, and the included ktest fragments. It integrates with ktest's console, power-cycle, post-install, and shared test-selection options.

## Risks And Edge Cases

The file uses `.kmx` in comments and paths; many VMware Linux configurations use `.vmx`, so users must verify actual VM file naming. Placeholder values will produce invalid paths if left unchanged. `vmrun reset` is abrupt. Serial-pipe setup must choose server/from-VM options correctly or ktest will hang waiting for console output.

## Test Signals

Dry-run should show the ncat Unix-socket console and `vmrun` reset command after placeholders are replaced. Runtime validation includes readable serial output, successful `dracut` post-install, and a forced VMware reset after configured reboot timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/examples/vmware.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/ktest.pl -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/ktest.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/sample.conf -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/ktest/sample.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit-completion.sh -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit-completion.sh

## Purpose

This shell script provides bash completion for the KUnit command-line tool. It completes top-level subcommands and option flags by asking the local `kunit.py` script for hidden `--list-cmds` and `--list-opts` output.

## Important APIs, Types, And Data

It defines `_kunit_dir` from `${BASH_SOURCE[0]}` and a completion function `_kunit()`. It uses bash-completion's `_init_completion` to populate `cur`, `prev`, `words`, and `cword`. It invokes `${_kunit_dir}/kunit.py --list-cmds`, `${script} ${words[1]} --list-opts`, or `${script} --list-opts`, then fills `COMPREPLY` via `compgen -W`. It registers completions for `kunit.py`, `kunit`, and `./tools/testing/kunit/kunit.py`.

## Control Flow

On completion, `_kunit()` initializes completion state. If completing the first non-option word, it lists subcommands. If completing an option after a subcommand, it lists options for that subcommand; otherwise it lists root options. Non-option arguments beyond the command are left to bash's default completion because the function returns without setting `COMPREPLY`.

## State And Persistence Behavior

The script has no persistent state. Runtime state is limited to shell variables and `COMPREPLY`. It depends on the current checkout's `kunit.py` output each time completion runs, so option lists track parser changes without manual duplication.

## Dependencies And Integration Points

It depends on bash, bash-completion's `_init_completion`, executable Python `kunit.py`, and `kunit.py`'s hidden `--list-cmds`/`--list-opts` behavior. It integrates with shells that source this file and commands named `kunit.py`, `kunit`, or the relative tool path.

## Risks And Edge Cases

If bash-completion is not installed, `_init_completion` is missing and the function silently returns. The script does not quote `${words[1]}` in the command invocation, but subcommands are parser-defined simple words. Completion can be slow if `kunit.py` startup is slow. Errors from `kunit.py` are discarded, so broken parsers produce empty completions.

## Test Signals

Source the script in bash and run `complete -p kunit.py`. `COMP_WORDS`-driven manual tests or interactive tab completion should show `run config build exec parse` at the command position and appropriate parser options after a subcommand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit-completion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit.py

## Purpose

`kunit.py` is the main command-line frontend for configuring, building, executing, parsing, and reporting Linux KUnit tests. It wraps `kunit_kernel.LinuxSourceTree` for build/run operations, `kunit_parser` for KTAP parsing, and `kunit_json` for optional JSON output.

## Important APIs, Types, And Data

Data types include `KunitStatus`, `KunitResult`, `KunitConfigRequest`, `KunitBuildRequest`, `KunitParseRequest`, `KunitExecRequest`, and `KunitRequest`. Major functions are `config_tests()`, `build_tests()`, `config_and_build_tests()`, `exec_tests()`, `parse_tests()`, `run_tests()`, `tree_from_args()`, command handlers for `run`, `config`, `build`, `exec`, and `parse`, and parser builders `add_common_opts()`, `add_build_opts()`, `add_exec_opts()`, and `add_parse_opts()`. Hidden completion options are `--list-cmds` and `--list-opts`.

## Control Flow

`main()` builds an argparse tree, massages pseudo-boolean flags such as `--json` and `--raw_output`, changes to the kernel root, handles completion listing, then dispatches to the selected subcommand. `run` creates the build directory if needed, configures, builds, executes, and parses. `config` only regenerates `.config`; `build` configures and builds; `exec` runs an already-built kernel and parses/list-tests as requested; `parse` reads stdin or a file and parses saved output. `exec_tests()` also supports listing tests/attributes/suites and isolated per-test or per-suite execution.

## State And Persistence Behavior

Persistent state is mainly in the build directory: `.kunitconfig`, `.config`, `last_used_kunitconfig`, `test.log`, build outputs, and optional JSON result files. `parse` can write JSON to a named file or stdout. The process exits with status 1 on config/build/test failure, making it suitable for CI.

## Dependencies And Integration Points

It depends on Python 3.7+, `argparse`, `os`, `re`, `shlex`, `time`, `kunit_kernel`, `kunit_parser`, `kunit_json`, and `kunit_printer`. It integrates with Linux source layout by deriving the root from `tools/testing/kunit`, with `KBUILD_OUTPUT` for default build directories, with QEMU/UML options, and with shell completion through hidden list options.

## Risks And Edge Cases

The parser uses hidden private argparse internals for option listing. `get_kernel_root_path()` exits if the script path does not contain `tools/testing/kunit`, which can surprise copied or symlinked invocations. `--json` and `--raw_output` require argument massaging to avoid argparse ambiguity. Listing tests uses KUnit executor output filtering and has a comment-level hack to drop a dummy TAP header. Isolated runs can be expensive because each suite/test boots separately.

## Test Signals

Existing tests in `kunit_tool_test.py` cover much of the parser and CLI behavior. Manual validation includes `kunit.py --list-cmds`, `kunit.py run --list_tests`, `kunit.py parse --file <log>`, `kunit.py run --json=stdout`, and failure exit-code checks for broken configs or failing KTAP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_config.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_config.py

## Purpose

This module parses, represents, compares, merges, and writes Kconfig fragments used by the KUnit tooling. It gives `kunit_kernel.py` a structured way to manage `.kunitconfig`, `.config`, architecture config fragments, and user-added Kconfig options.

## Important APIs, Types, And Data

Regex constants are `CONFIG_IS_NOT_SET_PATTERN` and `CONFIG_PATTERN`. `KconfigEntry` is a frozen dataclass with `name` and `value` and stringifies to either `CONFIG_NAME=value` or `# CONFIG_NAME is not set` for value `n`. `KconfigParseError` reports invalid non-comment lines. `Kconfig` stores `_entries: Dict[str, str]` and provides `as_entries()`, `add_entry()`, `is_subset_of()`, `conflicting_options()`, `merge_in_entries()`, and `write_to_file()`. Module-level helpers are `parse_file()` and `parse_from_string()`.

## Control Flow

`parse_from_string()` strips each line, skips blanks and comments, matches enabled/value assignments, matches `not set` comments as value `n`, and raises `KconfigParseError` for unrecognized non-comment content. Merge and subset operations are simple dictionary walks. `write_to_file()` opens with append mode and writes all entries in iteration order.

## State And Persistence Behavior

`Kconfig` state is in-memory until `write_to_file()` appends it to a target path. The append behavior is intentional for some call sites but requires callers such as `kunit_kernel.build_config()` to remove old files before writing when replacement semantics are needed. Entry ordering follows Python dict insertion order from parse/merge order.

## Dependencies And Integration Points

It depends only on dataclasses, regex, and typing. It integrates with `kunit_kernel.get_parsed_kunitconfig()`, architecture config merging, validation of generated `.config` files, and `--kconfig_add` parsing. Tests in `kunit_tool_test.py` exercise parsing, subset checks, and conflict behavior.

## Risks And Edge Cases

The parser accepts `CONFIG_FOO=` values matching `\S+` or quoted strings, but not every possible Kconfig syntax nuance. Comments other than `# CONFIG_X is not set` are ignored, so explanatory comments are not preserved. `is_subset_of()` treats absent `n` entries as satisfied, which matches Kconfig absence semantics but can hide explicit off-options in some comparisons. `write_to_file()` appends, so callers must manage truncation.

## Test Signals

Unit tests should parse enabled, quoted, and disabled entries; reject invalid lines; verify conflict detection; verify absent `n` subset behavior; and confirm append/write formatting. Integration signals are successful KUnit config generation and clear missing-option diagnostics when Kconfig dependencies prevent requested options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_json.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_json.py

## Purpose

This module converts parsed KUnit `Test` trees into JSON shaped for KernelCI-style test reporting. It is used when `kunit.py` receives `--json` during run, exec, or parse commands.

## Important APIs, Types, And Data

`Metadata` is a dataclass carrying `arch`, `def_config`, and `build_dir`. `JsonObj` aliases `Dict[str, Any]`. `_status_map` maps parser statuses `SUCCESS`, `SKIPPED`, and `TEST_CRASHED` to `PASS`, `SKIP`, and `ERROR`; any other status becomes `FAIL`. `_get_group_json()` recursively converts a `Test` node into a group with `name`, `sub_groups`, `test_cases`, and `misc` count data. `get_json_result()` injects common metadata fields and returns pretty-printed JSON.

## Control Flow

`get_json_result()` builds common fields from metadata, calls `_get_group_json()` on the parsed root test, renames the top group to `KUnit Test Group`, and serializes with `json.dumps(indent=4)`. `_get_group_json()` partitions child tests into nested groups when a child has subtests, or leaf test cases otherwise, and appends aggregate counts from the parser's `TestCounts`.

## State And Persistence Behavior

The module has no persistent state. It returns a JSON string; `kunit.py` decides whether to print it or write it to a file. Several common metadata fields are intentionally set to `None` or fixed values such as `git_branch: kselftest`.

## Dependencies And Integration Points

It depends on `kunit_parser.Test` and `TestStatus`, standard `json`, dataclasses, and typing. It integrates with `kunit.py parse_tests()` and downstream systems expecting KernelCI-like fields such as `arch`, `defconfig`, `build_environment`, `sub_groups`, `test_cases`, and status strings.

## Risks And Edge Cases

Status mapping defaults all unrecognized statuses to `FAIL`, so `NO_TESTS` and parser failures collapse into failure rather than a more specific category. The top-level name is overwritten, which discards the parser's internal root name. Metadata is sparse and may not satisfy all KernelCI consumers without enrichment. Deeply nested or malformed `Test` trees are serialized recursively without cycle protection.

## Test Signals

Tests should verify pass/fail/skip/crash status mapping, nested group conversion, count fields, top-level naming, and file/stdout behavior through `kunit.py --json`. JSON validation with `json.loads()` and expected keys is sufficient for this module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_json.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_kernel.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_kernel.py

## Purpose

This module owns the low-level KUnit kernel configuration, build, and execution operations for both UML and QEMU-backed architectures. It abstracts make invocation, Kconfig merging/validation, process startup, output capture, timeout enforcement, and interrupt cleanup behind `LinuxSourceTree`.

## Important APIs, Types, And Data

Constants define KUnit paths such as `.config`, `.kunitconfig`, `last_used_kunitconfig`, default/all-tests/UML config fragments, `test.log`, and QEMU config directories. Exceptions are `ConfigError` and `BuildError`. Operation classes are `LinuxSourceTreeOperations`, `LinuxSourceTreeOperationsQemu`, and `LinuxSourceTreeOperationsUml`; the public orchestrator is `LinuxSourceTree`. Helpers include `get_kconfig_path()`, `get_kunitconfig_path()`, `get_old_kunitconfig_path()`, `get_parsed_kunitconfig()`, `get_outfile_path()`, `_default_qemu_config_path()`, and `_get_qemu_ops()`.

## Control Flow

`LinuxSourceTree.__init__()` chooses UML by default or loads a QEMU config module for non-UML architectures, parses and merges requested kunitconfig fragments, and adds `--kconfig_add` entries. `build_reconfig()` reuses an existing `.config` only if it contains the requested KUnit options and the remembered `last_used_kunitconfig` matches; otherwise it removes and regenerates `.config`. `build_kernel()` runs olddefconfig and `make all compile_commands.json scripts_gdb`. `run_kernel()` builds kernel command-line KUnit filters, starts UML or QEMU, tees output to `test.log`, yields lines to the parser, and uses a background waiter to terminate on timeout.

## State And Persistence Behavior

Persistent state lives in the build directory: `.kunitconfig`, `.config`, `last_used_kunitconfig`, `test.log`, `linux`/kernel images, build products, and generated compile/debug artifacts. The class also keeps in-memory `_process` state while the kernel is running and restores terminal settings after process completion or SIGINT.

## Dependencies And Integration Points

It depends on `subprocess`, `os`, `shlex`, `shutil`, `signal`, `threading`, dynamic import machinery, `kunit_config`, and `qemu_config`. It integrates with make, UML binaries, `qemu-system-*`, architecture-specific `tools/testing/kunit/qemu_configs/*.py`, Linux Kbuild `O=`, KUnit kernel command-line flags, and `kunit.py` request handling.

## Risks And Edge Cases

QEMU config loading mutates `extra_qemu_params` on the imported `QEMU_ARCH` object, so repeated construction with extra args can accumulate if the same module object is reused. `run_kernel()` writes leftover stdout in `finally`, which is good for logs but depends on callers consuming the generator or closing it. Timeout handling terminates the process from a background thread and prints generic exceptions. `build_config()` uses append-mode Kconfig writes and relies on prior file removal for clean replacement. Non-UML QEMU assumes acceleration fallbacks and kernel paths are valid for the selected arch.

## Test Signals

Unit tests should mock `subprocess` for make/UML/QEMU command construction, verify kunitconfig merge/conflict/validation paths, ensure repeated `run_kernel()` calls do not mutate caller args, and test timeout cleanup. Integration tests are `kunit.py config`, `build`, `exec --raw_output=all`, architecture listing with `--arch=help`, and validation that `test.log` captures the same kernel output sent to the parser.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_kernel.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_parser.py -->
# sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_parser.py

## Purpose

This module extracts KTAP/TAP from kernel output, parses KUnit results into a nested `Test` tree, tracks aggregate pass/fail/skip/crash/error counts, and prints human-readable summaries. It is the central result parser for `kunit.py`.

## Important APIs, Types, And Data

Core data types are `Test`, `TestStatus`, `TestCounts`, and `LineStream`. Regex constants recognize KTAP/TAP starts, kernel-output stops, executor errors, subtest headers, test plans, test result lines, skip directives, and diagnostic lines. Important functions include `extract_tap_lines()`, `check_version()`, `parse_ktap_header()`, `parse_test_header()`, `parse_test_plan()`, `parse_test_result()`, `parse_diagnostic()`, print/format helpers, `_summarize_failed_tests()`, `bubble_up_test_results()`, `parse_test()`, and `parse_run_tests()`.

## Control Flow

`parse_run_tests()` prints a divider, calls `extract_tap_lines()` to isolate TAP from mixed kernel logs, and either reports missing KTAP or calls recursive `parse_test()`. `parse_test()` handles three forms: a top-level KTAP/TAP header and plan, a nested subtest with optional KTAP and/or `# Subtest`, or a leaf `ok`/`not ok` result. It consumes diagnostics between structural lines, recurses through expected subtests, checks matching result numbers/names, bubbles child counts up, prints incremental results, and returns a populated root test.

## State And Persistence Behavior

The parser itself has no file persistence. It stores parse state in `LineStream`, `Test.log`, `Test.subtests`, `Test.counts`, and `Test.status`. Printing happens incrementally through a `Printer`, and `kunit.py` uses the returned tree for summary status and JSON output.

## Dependencies And Integration Points

It depends on Python regex, textwrap, enums, dataclasses, typing, and `kunit_printer.Printer`. It integrates with `kunit_kernel.run_kernel()` output, `kunit.py parse_tests()`, `kunit_json`, `--summary`, `--failed`, `--raw_output=kunit`, and KUnit executor output including KTAP version 1 and TAP versions 13/14.

## Risks And Edge Cases

Parsing is intentionally tolerant but complex. It must handle prefixed kernel lines, missing headers, zero-test plans, nested suites, missing subtest result lines, mismatched test numbers, skipped tests, crashes, executor errors before KTAP, and kernel termination markers. `check_version()` has a typo in an error string (`higer`) but behavior is clear. If a top-level stream contains non-KTAP output before a version line, it is ignored except executor errors; users need `--raw_output=all` for full debugging. Failure summarization suppresses very large failure lists.

## Test Signals

`kunit_tool_test.py` includes extensive parser fixtures. Key regression signals are successful parsing of nested KTAP, TAP 13/14, skip directives, missing KTAP, missing subtest results, zero tests, crash logs, line-number preservation, failed-only printing, and summary/count status precedence where crashes outrank failures and failures outrank skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/kunit/kunit_parser.py -->
