# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-again.sh

Purpose: reruns an existing rcutorture result directory, optionally changing boot arguments, duration, link/copy mode, remote mode, and output directory.

Important APIs and functions: parses options with `checkarg`, copies or reuses old run directory, removes old runtime artifacts, transforms each `qemu-cmd` via `kvm-transform.sh`, reconstructs batch commands from the old `scenarios` file, and calls `kvm-end-run-stats.sh`.

Control flow: validate kernel tree and old run, determine suite, set result directory, copy/link old run unless inplace, transform qemu commands, generate a run-batches script, optionally dryrun, otherwise execute batches from new rundir and summarize.

State and persistence: creates a new result directory or mutates old one for inplace modes; writes `re-run`, log, transformed qemu commands, and fresh console/qemu outputs.

Dependencies and integration: depends on old run metadata `scenarios` and `torture_suite`, plus qemu command comments.

Risks and test signals: inplace modes can overwrite prior run artifacts. Bootarg transformation assumes single-line qemu commands and simple whitespace.
