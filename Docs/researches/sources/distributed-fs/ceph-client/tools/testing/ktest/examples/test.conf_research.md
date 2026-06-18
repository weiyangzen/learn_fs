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
