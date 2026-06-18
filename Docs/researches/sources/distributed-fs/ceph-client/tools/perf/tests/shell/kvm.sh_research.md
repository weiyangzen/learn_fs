<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kvm.sh -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/kvm.sh

## Purpose

This shell test validates `perf kvm` stat, record/report, buildid-list, and live stat modes against a minimal QEMU/KVM process.

## Research

`setup_qemu` chooses a qemu-system binary by architecture, skips if qemu or `/dev/kvm` access is missing, probes permission with `perf kvm stat record -a`, then starts qemu daemonized with KVM, no display, no monitor, and a pidfile. `test_kvm_stat` records KVM events for that pid and requires `VM-EXIT` in stat report. `test_kvm_record_report` starts `perf kvm --host record -p` in the background, interrupts it, and requires `Event count` in report. `test_kvm_buildid_list` expects buildid-list output. `test_kvm_stat_live` runs live stat under timeout and greps a percentage. State includes qemu process, pidfile, perf data, and live log; cleanup kills qemu. Dependencies are QEMU, KVM access, perf KVM events, timeout, and host symbols. Risks include qemu failing without a machine/kernel, permission skips, live output timing, and background recorder interruption races. Passing signal is all KVM subcommands producing expected output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/kvm.sh -->
