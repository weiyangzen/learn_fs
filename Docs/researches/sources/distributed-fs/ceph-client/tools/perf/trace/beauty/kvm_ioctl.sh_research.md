# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/kvm_ioctl.sh

Purpose: Builds the KVM ioctl command name table consumed by `ioctl.c`.

Important APIs/types/functions: It parses `KVM_*` `_IO`, `_IOR`, `_IOW`, and `_IOWR` definitions from `kvm.h` and emits `static const char *kvm_ioctl_cmds[]` indexed by ioctl number.

Control flow: The script selects a header directory, greps for `KVMIO`-based definitions with hexadecimal command numbers, strips unsupported or intentionally excluded architecture/debug commands, sorts the result, and formats array entries.

State and persistence: Output is stdout-generated C only.

Dependencies and integration points: The generated array is included in `ioctl__scnprintf_kvm_cmd`. Build correctness depends on UAPI `tools/include/uapi/linux/kvm.h` and standard text utilities.

Risks: The explicit exclusion list can hide valid commands if perf later wants broader KVM coverage. Regex drift can miss macros with nonstandard formatting.

Test signals: Regenerate the array, compile perf, and trace a KVM fd issuing common ioctls such as create VM/VCPU to verify `KVM_*` names appear.
