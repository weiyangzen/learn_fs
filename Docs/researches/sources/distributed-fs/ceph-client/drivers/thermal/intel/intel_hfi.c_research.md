# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_hfi.c

## Purpose

`intel_hfi.c` implements Intel Hardware Feedback Interface support. It allocates HFI tables per package, enables hardware when thermal netlink clients are present, processes package thermal HFI update interrupts, and publishes CPU performance/efficiency capabilities to userspace.

## Important APIs, Types, and Functions

Important types are `struct hfi_cpu_data`, `struct hfi_hdr`, `struct hfi_instance`, `struct hfi_features`, and per-CPU `struct hfi_cpu_info`. Public functions are `intel_hfi_init()`, `intel_hfi_online()`, `intel_hfi_offline()`, and `intel_hfi_process_event()`. `hfi_parse_features()` reads CPUID leaf 6. `update_capabilities()` emits `thermal_genl_cpu_capability_event()` in chunks. Syscore and thermal notifier callbacks enable/disable HFI across suspend and netlink bind/unbind.

## Control Flow

Initialization parses feature layout, allocates package instances and cpumasks, creates a workqueue, registers thermal netlink notifier, and syscore PM ops. CPU online links the CPU to a package instance, allocates hardware/local tables for first package use, initializes locks/work, and enables HFI when clients exist. Interrupt processing acknowledges only new timestamps, copies the hardware table under locks, clears the package HFI status bit, and queues delayed netlink publication.

## State and Persistence Behavior

Global state tracks package instances, feature layout, client count, and workqueue. Per-package state owns hardware table pages, local copy, cpumask, and locks. Hardware table pages are intentionally not freed on normal CPU offline because some processors remember table addresses.

## Dependencies and Integration Points

It depends on CPUID/MSRs, topology package IDs, CPU hotplug calls from `therm_throt.c`, package thermal interrupt clearing, syscore PM, and thermal generic netlink. `thermal_interrupt.h` supplies package status clear.

## Risks and Test Signals

Risks include package/die topology assumptions, memory retained for hardware table reuse, client-count underflow on notifier imbalance, delayed work after offline/suspend, and concurrent table copy versus netlink reads. Test signals include HFI CPUID parsing, CPU online/offline package transitions, thermal netlink bind/unbind enabling, package HFI interrupt ack with duplicate timestamp, suspend/resume, and multi-package capability event chunking.
