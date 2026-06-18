<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gcc-thunk-extern.sh -->
# sources/distributed-fs/ceph-client/arch/s390/tools/gcc-thunk-extern.sh

Purpose: This shell probe checks whether the compiler can build s390 external indirect-branch/function-return thunks without a section type conflict for a cold init-text caller.

Important APIs/types/functions: It is a `/bin/sh` script that feeds a small C translation unit to the compiler command passed as `$@`, using flags `-fno-PIE`, `-march=z10`, `-mindirect-branch=thunk-extern`, `-mfunction-return=thunk-extern`, `-mindirect-branch-table`, `-O2`, and `-c -o /dev/null`.

Control flow: The script writes the C source on stdin via heredoc and exits with the compiler's status. The C sample defines `put_page()` and an `.init.text` cold function calling it twice, reproducing the conflict the probe is meant to detect.

State and persistence: It creates no persistent files because output goes to `/dev/null`. Its result is used by build configuration/probing logic.

Dependencies and integration points: It depends on a GCC-compatible s390 compiler supporting the thunk flags. It integrates with s390 mitigation flag selection.

Risks and test signals: Probe accuracy depends on the sample matching the compiler bug/feature being tested. Tests include running it with supported/unsupported compiler versions and verifying build logic accepts or rejects thunk-extern flags accordingly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/tools/gcc-thunk-extern.sh -->
