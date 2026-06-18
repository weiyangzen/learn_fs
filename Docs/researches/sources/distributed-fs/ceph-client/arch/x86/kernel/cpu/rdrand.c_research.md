# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/rdrand.c

## Purpose

This file validates the CPU RDRAND instruction during CPU initialization and disables RDRAND/RDSEED capability bits if the instruction appears unreliable. The check protects kernel and userspace consumers from known classes of hardware or firmware failures that return repeated values or fail the instruction.

## Important APIs, Types, And Functions

The single API is `x86_init_rdrand(struct cpuinfo_x86 *c)`. It uses `rdrand_long()`, `cpu_has()`, `clear_cpu_cap()`, and `pr_emerg()`. The local sampling constants require eight samples and at least five observed changes.

## Control Flow

If the CPU lacks `X86_FEATURE_RDRAND`, the function exits. Otherwise it invokes RDRAND repeatedly, records whether each call succeeded, and counts sample-to-sample changes. Any failed invocation or too few changed samples marks the feature unreliable. On failure it clears both `X86_FEATURE_RDRAND` and `X86_FEATURE_RDSEED` from the CPU capability set and logs an emergency message.

## State, Dependencies, And Integration

The persistent effect is in the in-memory CPU capability bitmap for the current CPU initialization path. The file depends on x86 processor feature handling, `asm/archrandom.h`, and printk. It integrates with CPU bring-up and affects later random-number instruction dispatch.

## Risks And Test Signals

The heuristic intentionally catches obvious bad outputs, not cryptographic quality. False positives disable hardware random instructions; false negatives leave bad hardware exposed. Test by booting with known-good and fault-injected RDRAND behavior, checking dmesg for the disable message, and verifying `/proc/cpuinfo` feature flags no longer show RDRAND/RDSEED after failure.
