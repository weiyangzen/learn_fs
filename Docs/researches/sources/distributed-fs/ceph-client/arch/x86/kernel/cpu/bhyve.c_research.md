# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/bhyve.c

## Purpose
This file implements FreeBSD bhyve hypervisor detection and guest enlightenments.

## Important APIs, Types, and Functions
`bhyve_detect()` verifies the hypervisor CPUID feature, finds the `"bhyve bhyve "` CPUID base, and records the max leaf. `bhyve_features()` reads feature leaf `0x40000001`. `bhyve_ext_dest_id()` reports MSI extended destination ID support. `bhyve_x2apic_available()` always returns true. `x86_hyper_bhyve` registers the hypervisor descriptor.

## Control Flow
During hypervisor probing, detection stores CPUID base/max values. Feature callbacks later validate that the feature leaf is present before reading feature bits. Platform init is a noop, but x2APIC is advertised as available and MSI extended destination ID is conditional on CPUID.

## State and Persistence
Persistent state is limited to `bhyve_cpuid_base` and `bhyve_cpuid_max` after detection.

## Dependencies and Integration Points
The file depends on x86 hypervisor CPUID helpers, CPU feature detection, and the generic `hypervisor_x86` registration framework. It integrates with APIC/x2APIC and MSI destination-ID policy through descriptor callbacks.

## Risks and Test Signals
Risks include false detection if the signature or CPUID ranges are mishandled, or advertising x2APIC/MSI capabilities not supported by the host. Test signals include bhyve guest boot detection, CPUID feature leaf behavior, x2APIC availability decisions, and MSI routing tests with extended destination IDs.
