# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/perfctr-watchdog.c

## Purpose

This file provides a small reservation layer for performance counter MSRs used by the local APIC NMI watchdog and other low-level users. It is not a full watchdog implementation; it coordinates ownership of counter and event-select MSR slots so independent kernel subsystems do not program the same hardware counter at the same time.

## Important APIs, Types, And Functions

The exported APIs are `reserve_perfctr_nmi()`, `release_perfctr_nmi()`, `reserve_evntsel_nmi()`, and `release_evntsel_nmi()`. The state is held in two static bitmaps, `perfctr_nmi_owner` and `evntsel_nmi_owner`, each sized by `NMI_MAX_COUNTER_BITS`. Translation helpers `nmi_perfctr_msr_to_bit()` and `nmi_evntsel_msr_to_bit()` convert vendor/family-specific MSR numbers into bitmap indices using `boot_cpu_data`, architectural perfmon feature bits, and legacy AMD, Intel P6/KNC/P4, Zhaoxin, and Centaur ranges.

## Control Flow

Reservation calls translate the MSR to a slot, treat unmanaged MSRs as available, and then use `test_and_set_bit()` to atomically claim the bit. Release calls translate the MSR and clear the corresponding bit. No locks are used; atomic bit operations are the synchronization mechanism.

## State, Dependencies, And Integration

The bitmap state is boot-lifetime only and not persistent. Consumers coordinate with the NMI watchdog/perf counter hardware through these exported symbols. Dependencies include x86 CPU vendor data, perf event MSR constants, APIC/NMI headers, bitops, and export support.

## Risks And Test Signals

The translation logic is hardware-specific. Incorrect offsets can alias unrelated counters or make a managed counter appear unmanaged. The boundary check uses `counter > NMI_MAX_COUNTER_BITS`; index equality with the bitmap size would be out of range if ever produced. Useful tests are booting on supported vendors, enabling the NMI watchdog alongside perf users, and verifying duplicate reservations fail while unrelated counters can still be acquired and released.
