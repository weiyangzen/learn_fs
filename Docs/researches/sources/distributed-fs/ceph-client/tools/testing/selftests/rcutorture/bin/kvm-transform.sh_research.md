# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-transform.sh

Purpose: rewrites an existing single-line `qemu-cmd` for reruns by changing kernel image, serial console log, jitter directory, duration, and selected boot arguments.

Important APIs and functions: builds an awk program from replacement boot arguments, handles qemu-cmd comments for `seconds`, `TORTURE_JITTER_START`, and `TORTURE_JITTER_STOP`, and transforms `-serial`, `-kernel`, and `-append` fields.

Control flow: validate image, console log, jitter dir, and numeric duration; construct arrays of replacement boot args and parameters; run awk over stdin and emit transformed qemu-cmd to stdout.

State and persistence: no direct file writes except temp awk program; caller redirects output.

Dependencies and integration: used by `kvm-again.sh`.

Risks and test signals: assumes qemu command is one line with no whitespace in filenames. Bootarg replacement is parameter-name based and warns in comments about untrusted input.
