# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/scripts/hmi.sh

Purpose: manual-style powerpc HMI injection script that uses xscom utilities to inject recoverable core FIR errors and checks kernel HMI handling through `dmesg`.

Important APIs/types/functions: shell functions and variables include `GETSCOM`, `PUTSCOM`, `expected_hmis`, and `COUNT_HMIS()`. It uses `ppc64_cpu`, `/sys/firmware/opal/msglog`, `/dev/kmsg`, and xscom `getscom/putscom`.

Control flow: the script locates xscom tools, expands SMT snooze delay, iterates chip/core pairs parsed from OPAL msglog, verifies the target FIR is zero, writes a recoverable error, then waits up to about a minute for the expected number of harmless HMI log messages.

State and persistence behavior: it mutates hardware FIR state and system SMT snooze delay, restoring snooze delay via `trap`. It writes marker lines to the kernel log and relies on kernel state outside the workspace.

Dependencies and integration points: requires OpenPOWER/skiboot xscom utilities, OPAL firmware paths, root-like hardware access, and a kernel that logs the expected HMI text.

Risks and test signals: parsing is intentionally fragile and marked as such. Failure is indicated by nonzero exit after missing xscom tools, nonzero FIR, injection failure, or insufficient HMI messages.
