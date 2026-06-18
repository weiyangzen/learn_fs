# sources/distributed-fs/ceph-client/drivers/hv/mshv_synic.c

## Purpose

`mshv_synic.c` manages MSHV SynIC interrupt setup, message dispatch, scheduler/intercept kicks, async hypercall completions, and doorbell port integration for root partitions.

## Important APIs, Types, and Functions

- `mshv_isr()` is the main MSHV SynIC interrupt handler.
- Doorbell helpers read queued ports from SynIC event rings and invoke registered port-table callbacks.
- Scheduler message handlers kick VPs from bitset or pair messages.
- Async completion handler completes a partition's async hypercall.
- Intercept handler routes opaque intercept and APIC EOI messages to VP wait queues or irq ack notifiers.
- `mshv_synic_init/exit()` configure per-CPU SynIC pages, SINT vector/IRQ, CPU hotplug, and reboot cleanup.
- `mshv_register_doorbell()` and `mshv_unregister_doorbell()` create/connect/disconnect Hyper-V doorbell ports.

## Control Flow

CPU online setup maps SIMP, SIEFP, and SIRBP pages from MSR-provided GPAs, enables percpu IRQs if needed, programs interception and doorbell SINTs, and enables SynIC globally. `mshv_isr()` reads the interception SINT message slot, tries doorbell, scheduler, async completion, then intercept handling, clears the message, memory barriers, and writes EOM if pending.

Doorbell messages drain the doorbell event ring, look up each port ID, and call the registered callback in interrupt context. Scheduler messages find partitions through the RCU hash and wake target VPs. Intercept messages either notify irqfd resamplers on APIC EOI or kick the VP whose intercept message page has been filled by Hyper-V.

## State and Persistence Behavior

Per-CPU `synic_pages` stores mapped SynIC pages. SINT vector and Linux IRQ are module globals. Doorbell port table entries persist until unregister. VP run state is updated by interrupt context through `kicked_by_hv`, `vp_signaled_count`, and wait queues.

## Dependencies and Integration Points

The file depends on Hyper-V MSRs, ACPI GSI setup on platforms without `HYPERVISOR_CALLBACK_VECTOR`, CPU hotplug, reboot notifiers, port ID table, eventfd ack notifications, partition lookup, and root hypercall wrappers for ports and ring-empty notifications.

## Risks and Edge Cases

Callbacks run in interrupt context and must not sleep. Doorbell event-ring tail storage comes from Hyper-V per-CPU state and missing pages are tolerated with debug logs. Partition/VP lookup occurs under RCU but VP array entries are used without extra locking based on lifecycle assumptions. Reboot notifier removes CPU hotplug state for root partitions. Incorrect EOM ordering can lose messages.

## Test Signals

Test CPU online/offline SynIC setup, SINT IRQ allocation paths, doorbell registration and MMIO-triggered callback, async hypercall completion, scheduler bitset/pair messages, APIC EOI resampler notification, opaque intercept VP wakeups, message-pending EOM behavior, and module exit/reboot cleanup.
