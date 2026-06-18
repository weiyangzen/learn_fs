# sources/distributed-fs/ceph-client/arch/s390/kvm/trace.h

## Purpose
Defines `kvm` trace-system events specific to s390 VCPU execution, SIE entry/exit, intercepted instructions/program interrupts, SIGP, DIAG, control-register operations, prefix/STAP/STFL/STSI/STHYI, storage-key instructions, and pfault handling.

## Important APIs, Types, And Functions
The file provides common VCPU trace macros (`VCPU_PROTO_COMMON`, `VCPU_FIELD_COMMON`, `VCPU_ASSIGN_COMMON`, `VCPU_TP_PRINTK`) and many `TRACE_EVENT` definitions: `kvm_s390_skey_related_inst`, major pfault init/done events, `kvm_s390_sie_enter`, `kvm_s390_sie_fault`, `kvm_s390_sie_exit`, instruction/program/validity intercepts, `kvm_s390_handle_sigp`, `kvm_s390_handle_sigp_pei`, `kvm_s390_handle_diag`, `kvm_s390_handle_lctl`, `kvm_s390_handle_stctl`, `kvm_s390_handle_prefix`, `kvm_s390_handle_stap`, `kvm_s390_handle_stfl`, `kvm_s390_handle_stsi`, `kvm_s390_handle_operexc`, and `kvm_s390_handle_sthyi`.

## Control Flow And State
This file records diagnostic state only. Events capture VCPU ID plus PSW mask/address, then add event-specific operands such as intercept code, instruction bytes, SIGP order, control-register range, or STSI selectors. It includes s390 decoder metadata to print symbolic instruction/intercept names.

## Dependencies And Integration
Depends on Linux tracepoints, s390 SIE/debug/disassembly headers, and generated symbolic tables for intercepts, SIGP orders, DIAG codes, and instruction decoding. Call sites are in privileged instruction, SIGP, intercept, SIE, and pfault paths.

## Risks And Test Signals
Risks include malformed trace headers, field type mismatches, stale symbolic decoders, and trace output that no longer matches call-site semantics. Test signals are compile-time trace generation, boot with tracing enabled, selective enablement of KVM trace events, and correlation of trace output with KVM guest intercept tests.
