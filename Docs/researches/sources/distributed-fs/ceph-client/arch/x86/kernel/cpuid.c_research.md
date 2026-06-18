# sources/distributed-fs/ceph-client/arch/x86/kernel/cpuid.c

## Purpose
Implements the `/dev/cpu/<n>/cpuid` character device, allowing userspace to read CPUID leaves on a selected online CPU.

## Important APIs, Types, And Functions
`struct cpuid_regs_done` bundles CPUID registers and a completion. `cpuid_read()` validates 16-byte reads and issues CPUID operations on the target CPU. `cpuid_open()` validates CPU existence, online state, and CPUID support. `cpuid_init()` registers major `CPUID_MAJOR`, class `cpuid`, and CPU hotplug device creation.

## Control Flow
Userspace seeks to a 64-bit position where low 32 bits become EAX and high 32 bits become ECX. Reads must be multiples of 16 bytes; each chunk schedules `cpuid_smp_cpuid()` on the minor-number CPU with `smp_call_function_single_async()`, waits for completion, copies four registers to userspace, increments the position, and repeats.

## State, Persistence, And Dependencies
Persistent state is the registered char device, device class, and dynamic CPU hotplug state ID. It depends on CPU hotplug, SMP calls, completions, uaccess, and CPUID helpers.

## Integration Points
Creates `/dev/cpu/%u/cpuid` nodes and integrates with CPU online/offline to add/remove devices.

## Risks
The target CPU can go offline after open or during read, returning errors from SMP calls. Count alignment is strict. Userspace-visible CPUID reflects kernel feature masking and CPU-specific CPUID state.

## Test Signals
Module load should create devices for online CPUs. Reads of 16-byte chunks should match native CPUID on the target CPU; odd sizes should return `-EINVAL`; offline or unsupported CPUs should fail open.
