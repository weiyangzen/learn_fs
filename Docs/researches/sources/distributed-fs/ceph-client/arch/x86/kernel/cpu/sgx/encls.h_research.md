# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/sgx/encls.h

## Purpose

This header wraps privileged SGX ENCLS instructions in C inline functions with Linux exception-table handling. It provides the low-level instruction interface used by native SGX, EPC reclaim, SGX2 operations, and KVM SGX virtualization.

## Important APIs, Types, And Functions

Helpers `encls_faulted()`, `encls_failed()`, `ENCLS_TRAPNR()`, and `ENCLS_WARN()` classify ENCLS return values. Assembly macros `__encls_ret_N()` and `__encls_N()` encode leaves that return error codes or fault-only status. Inline wrappers include `__ecreate()`, `__eextend()`, `__eadd()`, `__einit()`, `__eremove()`, `__edbgwr()`, `__edbgrd()`, `__etrack()`, `__eldu()`, `__eblock()`, `__epa()`, `__ewb()`, `__emodpr()`, `__emodt()`, `__eaug()`, and `__eupdatesvn()`.

## Control Flow

Each wrapper loads the ENCLS leaf number and operands into required registers, executes `encls`, and uses `_ASM_EXTABLE_TYPE(..., EX_TYPE_FAULT_SGX)` so faults are converted into encoded return values. Callers then decide whether a page fault is expected/retryable or whether to warn and fail.

## State, Dependencies, And Integration

The header does not own state; it changes SGX hardware state through ENCLS. Dependencies include x86 assembly helpers, exception tables, trap numbers, and SGX architectural structures. It is integrated across every SGX source file.

## Risks And Test Signals

Register constraints and fault classification are critical. A wrong wrapper can corrupt inputs or misreport hardware failures. Test with enclave create/add/init/remove, EPC reclaim/load, SGX2 page modification, debug read/write, KVM virtual ECREATE/EINIT, and injected invalid operands that should fault predictably.
