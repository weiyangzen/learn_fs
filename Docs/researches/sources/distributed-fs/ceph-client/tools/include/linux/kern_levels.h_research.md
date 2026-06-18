<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kern_levels.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/kern_levels.h

## Purpose
`kern_levels.h` defines kernel log-level string prefixes for tools logging compatibility.

## APIs And Flow
It exports `KERN_SOH`, `KERN_SOH_ASCII`, severity macros from `KERN_EMERG` through `KERN_DEBUG`, `KERN_DEFAULT`, and `KERN_CONT`. In this tools copy the prefixes are empty strings or empty character constants, so they do not encode kernel control bytes.

## State, Dependencies, Risks, Tests
There is no state and no dependencies. It integrates with `printk`-style macros that concatenate log level markers into format strings. Risks are loss of severity information in user-space output and portability of the empty character definition. Test signals are compile checks for every log-level macro and diagnostics proving user-space logging does not expose raw kernel control bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/kern_levels.h -->
