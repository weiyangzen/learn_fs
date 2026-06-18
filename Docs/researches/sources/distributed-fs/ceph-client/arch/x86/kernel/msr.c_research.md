# sources/distributed-fs/ceph-client/arch/x86/kernel/msr.c

Purpose: Implements the x86 `/dev/cpu/<n>/msr` character device for privileged userspace reads and writes of model-specific registers on online CPUs.

Important APIs/types/functions: module init/exit are `msr_init()` and `msr_exit()`. File operations are `msr_read()`, `msr_write()`, `msr_ioctl()`, and `msr_open()`. CPU hotplug callbacks create and destroy per-CPU devices. Module parameter `allow_writes` is handled by `set_allow_writes()` and `get_allow_writes()`.

Control flow: init registers fixed major `MSR_MAJOR`, creates the `msr` device class, and registers dynamic CPU hotplug state to create `/dev/cpu/%u/msr` devices. Open requires `CAP_SYS_RAWIO`, a valid online CPU, and CPU MSR support. Reads require 8-byte granularity, repeatedly call `rdmsr_safe_on_cpu()` at the file offset register number, and copy two u32 values to userspace. Writes enforce lockdown `LOCKDOWN_MSR`, apply the write policy filter, taint the kernel as CPU-out-of-spec, then call `wrmsr_safe_on_cpu()`. Ioctls provide register-array read/write variants.

State and persistence: persistent module state is CPU hotplug state id, registered char device/class, and `allow_writes` policy. Device nodes follow CPU online state. MSR writes change CPU hardware state and may persist until reset depending on the register.

Dependencies and integration points: depends on x86 MSR safe-on-CPU helpers, Linux device model, CPU hotplug, security lockdown, capability checks, kernel tainting, user-copy helpers, and `/dev/cpu` device-node naming.

Risks: MSR writes are inherently unsafe; default policy logs and taints but allows writes, while `allow_writes=off` blocks them and `on` suppresses warnings. Logging is rate-limited to avoid kmsg floods. CPU offline after open can still make safe MSR helpers fail. Lockdown blocks writes but not reads.

Test signals: tests should open devices only as `CAP_SYS_RAWIO`, reject offline/non-MSR CPUs, enforce 8-byte read/write counts, exercise read and ioctl paths, verify lockdown write denial, check `allow_writes=off/on/default`, CPU hotplug device creation/removal, and taint/warning behavior on writes.
