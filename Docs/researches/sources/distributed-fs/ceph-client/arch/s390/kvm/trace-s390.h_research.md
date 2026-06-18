# sources/distributed-fs/ceph-client/arch/s390/kvm/trace-s390.h

## Purpose
Defines tracepoints in the `kvm-s390` trace system for VM/VCPU lifecycle, interrupt injection and delivery, reset requests, channel I/O enablement, IBS/AIS mode changes, suppressed adapter interrupts, and gmap notifier activity.

## Important APIs, Types, And Functions
The file is a trace header using `TRACE_EVENT`. It defines symbolic interrupt-name helpers through `kvm_s390_int_type` and `get_irq_name()`. Events include `kvm_s390_create_vm`, `kvm_s390_create_vcpu`, `kvm_s390_destroy_vcpu`, `kvm_s390_vcpu_start_stop`, `kvm_s390_inject_vm`, `kvm_s390_inject_vcpu`, `kvm_s390_deliver_interrupt`, `kvm_s390_request_resets`, `kvm_s390_stop_request`, `kvm_s390_enable_css`, `kvm_s390_enable_disable_ibs`, `kvm_s390_modify_ais_mode`, `kvm_s390_airq_suppressed`, and `kvm_s390_gmap_notifier`.

## Control Flow And State
Tracepoints are passive instrumentation. Each event defines its prototype, captured fields, fast assignment, and print format. The only state persisted is trace-buffer data emitted by call sites elsewhere in KVM. The file sets `TRACE_SYSTEM` to `kvm-s390` and `TRACE_SYSTEM_VAR` to a valid C identifier, then includes `trace/define_trace.h` outside the include guard.

## Dependencies And Integration
Depends on Linux tracepoint infrastructure and KVM s390 interrupt constants. Integration occurs through generated trace headers included by KVM implementation files and consumed by ftrace/perf/tracefs tooling.

## Risks And Test Signals
Risks are ABI-like trace format churn, incorrect field widths, symbol mapping drift as interrupt constants change, and duplicate trace system definitions. Signals include successful trace header generation, compile coverage, enabling the events under tracefs, and confirming emitted lifecycle/interrupt/gmap messages during KVM test runs.
