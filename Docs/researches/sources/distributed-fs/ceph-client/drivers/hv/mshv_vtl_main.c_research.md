# sources/distributed-fs/ceph-client/drivers/hv/mshv_vtl_main.c

## Purpose
`mshv_vtl_main.c` implements the Microsoft Hyper-V VTL driver. It exposes privileged user-space interfaces for creating a VTL file descriptor, returning execution to lower VTLs, mapping per-CPU run/register pages, relaying selected SynIC/VMBus messages, issuing allowlisted hypercalls, and mapping VTL0 physical address space into a VTL2 process. The driver is tightly coupled to Hyper-V VSM/VTL register state and to the core VMBus interrupt path.

## Important APIs, types, and functions
Key file-local state includes `mshv_dev`, `mshv_vtl_sint_dev`, `mshv_vtl_hvcall_dev`, `mshv_vtl_low`, `mem_dev`, `msg_dpc`, `fd_wait_queue`, `flag_eventfds[]`, `mshv_vsm_page_offsets`, `mshv_vsm_capabilities`, and per-CPU `mshv_vtl_per_cpu`, `mshv_vtl_poll_file`, and `num_vtl0_transitions`.

Important types include `struct mshv_vtl`, `struct mshv_vtl_per_cpu`, `struct mshv_vtl_poll_file`, and `struct mshv_vtl_hvcall_fd`. Important entry points include `/dev/mshv` ioctls, anonymous VTL fd ioctls/mmap, `/dev/mshv_sint` read/poll/ioctls, `/dev/mshv_hvcall`, and `/dev/mshv_vtl_low`.

## Control flow
Module initialization registers `/dev/mshv`, initializes the message tasklet and waitqueue, queries VSM code-page offsets/capabilities, configures VSM partition protection, initializes the VTL return-call trampoline, installs a VTL-aware VMBus ISR, registers the SINT, hypercall, and low-memory misc devices, and creates a backing `mem_dev` for VTL0 memory remapping.

Per-CPU setup is driven by a CPU hotplug state in `hv_vtl_setup_synic()`. `MSHV_RETURN_TO_LOWER_VTL` disables preemption, handles pending guest-mode work, checks the per-CPU cancel flag with interrupts disabled, copies return actions into the VP assist page when supported, calls `mshv_vtl_return_call()`, and returns to user space on interrupt/intercept messages.

The custom ISR `mshv_vtl_vmbus_isr()` filters VTL2 SINT messages/events for user-space delivery, signals registered eventfds for event flags, and then calls the normal `vmbus_isr()`.

## State and persistence behavior
Most state is kernel-resident until module exit: miscdevice registrations, the memory device, global VSM capabilities, per-CPU run/register pages, eventfd registrations, and waitqueue/tasklet state. `mshv_vtl_ioctl_add_vtl0_mem()` intentionally keeps its `dev_pagemap` allocated after `devm_memremap_pages()` because VTL0 memory is not expected to be released independently from the VTL2 kernel. The hypercall allow bitmap is per file descriptor and is destroyed on close.

## Dependencies and integration points
This file depends on Hyper-V architecture helpers, SynIC MSRs, VP assist pages, VMBus interrupt plumbing, Linux miscdevice/anon-inode/eventfd/poll/mmap APIs, CPU hotplug, debug register and MTRR MSR accessors, and uapi structs from `uapi/linux/mshv.h`.

## Risks
The driver exposes powerful privileged surfaces: direct hypercalls, lower-VTL memory mapping, register/MSR access, and VTL execution transitions. Correct capability checks, mmap PFN validation, allow-bitmap enforcement, and copy-from-user bounds checks are critical. The hypercall path allocates input/output pages but does not check `__get_free_page()` failures before copying. CPU hotplug is assumed unsupported after CPU validation. The return path runs with preemption/interrupt constraints and can panic on unexpected Hyper-V entry reasons.

## Test signals
Useful validation signals include successful miscdevice registration, `MSHV_CHECK_EXTENSION` results, per-CPU mmap faults, VTL return/intercept delivery, SINT read/poll behavior across mask/unmask, eventfd signaling, rejection of non-admin hypercall/low-memory opens, rejection of disallowed hypercalls, VTL0 memory remap failures on invalid PFN ranges, and clean module teardown after partial initialization failures.
