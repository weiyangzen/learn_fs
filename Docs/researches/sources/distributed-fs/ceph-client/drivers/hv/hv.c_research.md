<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv.c -->
# sources/distributed-fs/ceph-client/drivers/hv/hv.c

## Purpose

`hv.c` provides low-level Hyper-V runtime services for the VMBus driver: per-CPU Hyper-V context allocation, hypervisor message posting, Synthetic Interrupt Controller page allocation and register programming, event-page cleanup during CPU hotplug, and channel CPU migration when a CPU goes offline.

## Important APIs, Types, and Functions

- `struct hv_context hv_context` is the exported global per-CPU Hyper-V context.
- `hv_init()` allocates `struct hv_per_cpu_context` storage.
- `hv_post_message()` formats `struct hv_input_post_message` and posts it via direct, nested, GHCB, or TDX hypercall paths.
- `hv_synic_alloc()` and `hv_synic_free()` allocate/free per-present-CPU SynIC message/event pages, paravisor pages, optional TDX post-message pages, and `hv_numa_map`.
- `hv_synic_init()` enables hypervisor and optional paravisor SynIC pages and interrupts and initializes the legacy synthetic timer.
- `hv_synic_cleanup()` migrates channels away from an offlined CPU when possible, waits for pending event bits to drain, disables SynIC/timer state, and disables per-CPU IRQs.
- `hv_hyp_synic_enable_regs()`, `hv_hyp_synic_disable_regs()`, and paravisor equivalents program SIMP, SIEFP, SINT, and SCONTROL registers.

## Control Flow

Initialization starts with `hv_init()`, then `hv_synic_alloc()` zeroes all per-CPU contexts and allocates the pages required for the current environment. Non-root, non-paravisor guests allocate hypervisor SynIC pages directly; root and paravisor environments memremap host-provided pages when enabling registers. Confidential VMBus additionally allocates encrypted paravisor SynIC pages. `hv_synic_init()` enables paravisor registers first when confidential, then enables hypervisor registers, enables interrupts through the correct controller, and sets up the synthetic timer.

Message posting disables local interrupts, chooses the per-CPU input page or TDX decrypted post-message page, copies the payload, and selects the hypercall path. CPU cleanup first refuses to offline the connect CPU while connected. For other CPUs it scans primary and sub-channels under `channel_mutex`, uses `vmbus_channel_set_cpu()` to migrate channels, waits briefly for event flags to clear, and then disables timer, SynIC pages, and IRQs.

## State and Persistence Behavior

The global `hv_context` persists for the VMBus lifetime. Per-CPU contexts hold SynIC message/event pages, tasklets, and optional paravisor/post-message pages. Allocation and freeing deliberately leak pages if encryption state cannot be restored safely. `hv_context.hv_numa_map` tracks CPU assignment for performance channels and is consumed by `channel_mgmt.c`. SynIC page pointers are temporarily set to memremapped host/paravisor pages while a CPU is online and cleared during disable.

## Dependencies and Integration Points

This file depends on architecture Hyper-V MSR and hypercall primitives from `<asm/mshyperv.h>`, per-CPU hypercall argument pages from `hv_common.c`, VMBus constants and tasklet callbacks from `hyperv_vmbus.h`, channel migration from `channel.c`, and timer setup from `clocksource/hyperv_timer.h`. It also calls weak isolation/paravisor hooks defined in `hv_common.c` and overridden by architecture code.

## Risks and Edge Cases

Encryption-state failures are handled by leaking memory, which is intentional but should remain visible in diagnostics. CPU offline can fail with `-EBUSY` if channels cannot migrate or event bits stay pending. The connect CPU cannot be offlined while VMBus is connected. Confidential VMBus sequencing is delicate: data must not be posted after interrupts are disabled, and hypervisor/paravisor register programming must stay in the documented order.

## Test Signals

Exercise boot and CPU hotplug on non-confidential, SNP, TDX, root, nested, and paravisor configurations; verify page encryption transitions; test `hv_post_message()` payload-size and isolation path selection; validate channel migration on CPU offline; and use lockdep/trace output to confirm event bits drain before cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv.c -->
