<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.h

## Purpose
Public libcpupower CPU frequency API header. It defines policy/list/stat structs and declares read, free, policy modification, frequency setting, stats, and generic table-read functions.

## Important APIs, Types, And Functions
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Control Flow
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## State And Persistence
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Dependencies And Integration Points
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Risks And Edge Cases
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.

## Test Signals
State ownership is explicit: many getters allocate linked lists or strings that must be released by corresponding `cpufreq_put_*` functions; write APIs mutate kernel cpufreq policy. Dependencies are C ABI consumers and `cpufreq.c`. Risks include linked-list nodes carrying a `first` backpointer that callers must not corrupt, zero/NULL return conventions requiring careful error handling, and API comments that may not cover all driver-specific sysfs absence cases. Test signals are ABI compile checks, leak tests for every getter/put pair, and write API behavior under unprivileged and privileged runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/cpufreq.h -->
