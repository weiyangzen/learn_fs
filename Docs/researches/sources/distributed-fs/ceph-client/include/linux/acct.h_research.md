<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acct.h -->
# sources/distributed-fs/ceph-client/include/linux/acct.h

## Purpose
`acct.h` provides kernel-side BSD process accounting definitions, version selection, lifecycle hooks, and time conversion helpers.

## Important APIs, types, and functions
When `CONFIG_BSD_PROCESS_ACCT` is enabled, it declares `acct_collect()`, `acct_process()`, and `acct_exit_ns()`. Otherwise they are no-op macros. It selects `ACCT_VERSION`, `AHZ`, and `acct_t` based on `CONFIG_BSD_PROCESS_ACCT_V3` and `CONFIG_M68K`. Inline helpers `jiffies_to_AHZ()` and `nsec_to_AHZ()` convert kernel time units into accounting ticks.

## Control flow
Accounting-enabled kernels collect exit data, write process records, and clean namespace accounting state through the declared hooks. Conversion helpers choose exact arithmetic paths where possible and use scaled division otherwise.

## State and persistence behavior
The header declares hooks for persistent accounting logs and namespace accounting state, but does not store state itself. The accounting record format is persistent ABI and depends on `ACCT_VERSION`.

## Dependencies and integration points
It includes UAPI accounting layouts and `linux/jiffies.h`, and integrates process exit, pid namespaces, and user tools that parse accounting records.

## Risks and test signals
Risks include record-format incompatibility, time conversion overflow/precision loss, and disabled-config stubs hiding accounting calls. Test signals include accton/process-exit tests, namespace teardown, record parser compatibility, and conversion tests for HZ/AHZ combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acct.h -->
