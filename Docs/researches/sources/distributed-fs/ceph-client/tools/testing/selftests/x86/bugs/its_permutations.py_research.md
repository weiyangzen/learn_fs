# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/bugs/its_permutations.py

## Purpose

`its_permutations.py` boots many virtme-ng kernels with combinations of `indirect_target_selection=`, `retbleed=`, and `spectre_v2=` command-line options, then runs `its_sysfs.py` inside each guest to validate sysfs mitigation reporting.

## Important APIs, Types, and Functions

It imports `subprocess`, `itertools`, `re`, `shutil`, `ksft`, and `common`. Important data are `default_kparam`, `BOOT_CMD`, `input_options`, and `TEST` pointing to `its_sysfs.py`. `pretty_print()` colorizes TAP and diagnostic output.

## Control Flow

The script skips if the host is not affected or if `vng` is unavailable. It computes the Cartesian product of all option values, sets a kselftest plan for the number of combinations, and for each combination builds a `vng --run <bzImage>` command with default panic/debugging parameters plus the tested mitigation parameters. It appends `-- <TEST>` to run the sysfs checker in the guest, waits for completion, reports pass on return code zero and fail otherwise, colorizes the captured output, appends it to `logs`, and writes `logs.txt` at the end.

## State and Persistence Behavior

The script writes `logs.txt` in the current working directory. virtme-ng may create its own temporary VM state. No kernel settings are changed on the host except through guest boots.

## Dependencies and Integration Points

It depends on virtme-ng, a built `arch/x86/boot/bzImage` relative to the test directory, `its_sysfs.py`, and the Python kselftest framework. It integrates command-line mitigation permutations with guest sysfs validation.

## Risks and Edge Cases

The command is executed through `shell=True` and is assembled as a string. Runtime is proportional to all option combinations, so it is expensive. The hardcoded bzImage path assumes an in-tree kernel build. `logs.txt` is overwritten in the working directory.

## Test Signals

Pass signals are one kselftest result per option combination, guest return code zero, readable pretty-printed `its_sysfs.py` output, and a final `ksft.finished()` summary.
