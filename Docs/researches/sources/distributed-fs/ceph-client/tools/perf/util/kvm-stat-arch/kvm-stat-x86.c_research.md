<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-x86.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-x86.c

## Purpose

`kvm-stat-x86.c` provides x86 KVM stat support for VM exits, MMIO, PIO, and MSR emulation timing, plus Intel-specific default event selection.

## Important APIs, Types, and Functions

It defines VMX and SVM exit-reason tables, common `exit_events`, `mmio_events`, `ioport_events`, `msr_events`, tracepoints `kvm_entry`, `kvm_exit`, `kvm_mmio`, `kvm_pio`, and `kvm_msr`, registered event ops for `vmexit`, `mmio`, `ioport`, and `msr`, skip event `"HLT"`, `__cpu_isa_init_x86()`, `__kvm_add_default_arch_event_x86()`, and exported table accessors.

## Control Flow

VM-exit duration uses common `kvm_exit` to `kvm_entry` pairing. MMIO write duration runs from `kvm_mmio` write to entry; MMIO read duration runs from exit to `kvm_mmio` read. PIO and MSR durations run from their tracepoint to entry. Decode functions format GPA plus R/W, port plus PIN/POUT, or MSR ECX plus R/W. ISA init chooses VMX for Intel and SVM for AMD/Hygon. Intel default-event logic adds `-e cycles` when the user did not provide an event or `--pfm-events`.

## State and Persistence Behavior

Static tables define supported events. Runtime state is in event keys and KVM stat ISA fields. Default event injection mutates argv by adding duplicated strings.

## Dependencies and Integration Points

It depends on x86 UAPI VMX/SVM/KVM exit macros, common KVM stat, x86 CPU detection, parse-options, and evsel field extraction.

## Risks and Edge Cases

MMIO read/write pairing is asymmetric and easy to regress. Intel default event selection avoids PEBS guest-sampling failure by not using `cycles:P`; tests should preserve that behavior. Unsupported vendor strings return `-ENOTSUP`. Tracepoint field-name changes break key extraction.

## Test Signals

Tests should cover Intel/AMD/Hygon vendor init, unknown vendors, vmexit decode, MMIO read and write pairing, PIO/MSR decode, HLT skipping, and default `cycles` insertion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/kvm-stat-arch/kvm-stat-x86.c -->
