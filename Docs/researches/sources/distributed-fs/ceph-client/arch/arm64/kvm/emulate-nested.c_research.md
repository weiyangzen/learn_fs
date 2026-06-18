# sources/distributed-fs/ceph-client/arch/arm64/kvm/emulate-nested.c

## Purpose

This file implements the arm64 KVM nested-virtualization trap triage and nested exception injection path. It maps architectural system-register encodings to coarse-grained trap controls, fine-grained trap controls, optional fine-grained filters, and main sysreg table indexes, then uses that metadata at runtime to decide whether a trapped access is handled by KVM or forwarded into a guest hypervisor.

## Important APIs, Types, And Functions

Key types are `enum trap_behaviour`, `struct trap_bits`, `enum cgt_group_id`, `union trap_config`, and `struct encoding_to_trap_config`. The large `encoding_to_cgt[]` and `encoding_to_fgt[]` tables describe forwarding rules for EL1, EL2, debug, PMU, trace, timer, cache, TLB, pointer-authentication, GIC CPU-interface, and FGT2 registers/instructions. `populate_nv_trap_config()` builds `sr_forward_xa`; `populate_sysreg_config()` attaches normal sysreg descriptor indexes. Runtime entry points include `triage_sysreg_trap()`, `forward_smc_trap()`, `forward_debug_exception()`, `kvm_emulate_nested_eret()`, `kvm_inject_nested_sync()`, `kvm_inject_nested_irq()`, `kvm_inject_nested_sea()`, and `kvm_inject_nested_serror()`.

## Control Flow

Boot/init code inserts table entries into an xarray keyed by sysreg encoding, validates duplicate mappings, checks FGT reserved-bit masks, and destroys the xarray on configuration errors. At trap time `triage_sysreg_trap()` decodes ESR, loads the trap config, rejects unavailable features through `kvm->arch.fgu`, applies FGT read/write group selection and filters, evaluates coarse or complex conditions, and either injects a nested sync exception or returns the sysreg table index for local handling. Nested ERET and exception injection temporarily put/load vCPU state to cross virtual EL1/EL2 contexts.

## State And Persistence Behavior

The xarray is persistent global metadata after initialization. Per-vCPU decisions read and mutate virtual EL2 sysregs, PSTATE, PC, exception flags, `ESR_EL2`, `FAR_EL2`, and PMU nested transition state. Nested injection may change the active virtual context and must run with preemption disabled around put/load boundaries.

## Dependencies And Integration Points

The file depends on arm64 sysreg encodings, `asm/kvm_nested.h`, `asm/kvm_emulate.h`, PMU helpers, timer helpers, pointer-authentication helpers, `hyp/adjust_pc.h`, xarray allocation, tracepoints, and the sysreg descriptor table populated elsewhere. `handle_exit.c` calls nested ERET and SMC/debug forwarding; sysreg handlers call `triage_sysreg_trap()`.

## Risks And Test Signals

Risks are table drift versus the architecture, duplicate/ranged encodings, wrong FGT polarity for negative bits, mishandled host-EL0-only forwarding, and missing put/load transitions when changing virtual EL. Test signals include nested sysreg trap forwarding, non-nested local handling, FGT-disabled feature UNDEF injection, nested IRQ filtering by `HCR_EL2.{TGE,IMO}`, ERETAx authentication failure behavior, SEA EASE routing, and boot logs for CGT/FGT counts or mask inconsistencies.
