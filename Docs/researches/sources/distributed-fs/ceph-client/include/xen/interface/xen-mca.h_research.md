# sources/distributed-fs/ceph-client/include/xen/interface/xen-mca.h

## Purpose
`xen-mca.h` defines the x86 Xen machine-check architecture ABI for fetching MCA logs, acknowledging entries, notifying affected domains, retrieving physical CPU information, injecting MSRs/MCEs for testing, and sharing Linux-compatible MCE log records.

## Important APIs, Types, and Functions
Important types include `mcinfo_common`, `mcinfo_global`, `mcinfo_bank`, `mcinfo_extended`, `mcinfo_recovery`, `mc_info`, `mcinfo_logical_cpu`, `xen_mc_fetch`, `xen_mc_notifydomain`, `xen_mc_physcpuinfo`, `xen_mc_msrinject`, `xen_mc_mceinject`, `xen_mc`, `xen_mce`, and `xen_mce_log`. Helpers include `x86_mcinfo_nentries`, `x86_mcinfo_first`, `x86_mcinfo_next`, and `x86_mcinfo_lookup`.

## Control Flow
Dom0 receives `VIRQ_MCA`, calls the MCA hypercall to fetch urgent or nonurgent error data, parses typed `mcinfo_*` entries, optionally notifies a guest domain, and acknowledges fetched records. Injection commands target CPUs for validation. The inline lookup helper scans the variable-sized entry list by type.

## State and Persistence Behavior
Xen maintains machine-check records and fetch IDs until acknowledged. `xen_mce_log` is a fixed-length in-memory ring-like log with overflow flag and finished markers; records are not persistent across reboot.

## Dependencies and Integration Points
It depends on x86 Xen arch hypercall numbering, VIRQ definitions, guest-handle macros, and Linux ioctl encoding. It integrates Xen with dom0 machine-check handling, mcelog-compatible consumers, CPU topology reporting, and hardware-error recovery workflows.

## Risks and Test Signals
Risks include parsing malformed or truncated variable-sized entries, failing to ACK fetched data, preserving `xen_mce` field offsets, injection privilege misuse, and recovery-action ambiguity. Test signals include injected MCE/MSR paths, urgent/nonurgent fetch/ack cycles, logical CPU info queries, overflow handling, and mcelog ABI compatibility.
