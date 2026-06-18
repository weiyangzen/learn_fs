# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/scattered.c

## Purpose

This file discovers CPU feature bits that are scattered across CPUID leaves rather than grouped in the usual architectural feature words. It centralizes the mapping from leaf/subleaf/register/bit to `X86_FEATURE_*` capability flags.

## Important APIs, Types, And Functions

`struct cpuid_bit` describes a feature, CPUID register, bit number, leaf, and subleaf. `cpuid_bits[]` includes features for APERF/MPERF, EPB, PPIN, APX, speculation controls, RDT monitoring/allocation, SGX subfeatures, AMD RAS/power/workload/topology features, ABMC, SDCIAE, and others. The single function is `init_scattered_cpuid_features(struct cpuinfo_x86 *c)`.

## Control Flow

The function walks the sorted table, checks that each CPUID leaf is valid by comparing against the maximum supported level for that CPUID namespace, calls `cpuid_count()`, and sets the target CPU capability when the requested register bit is present.

## State, Dependencies, And Integration

State changes are limited to the `cpuinfo_x86` capability bitmap. Dependencies include CPUID helpers, feature definitions, and CPU initialization. Later code such as resctrl and SGX relies on these features being set before capability-based initialization runs.

## Risks And Test Signals

Table ordering and leaf validity checks matter. A wrong register/bit maps hardware incorrectly, and duplicate feature entries for Intel/AMD leaves must remain intentional. Test by comparing `/proc/cpuinfo` flags and kernel capability-dependent behavior on CPUs with RDT, SGX, AMD extended features, and older CPUs that lack the leaves.
