# sources/distributed-fs/ceph-client/init/main.c

## Purpose
`init/main.c` is the kernel boot orchestration file. It implements `start_kernel()`, command-line and bootconfig parsing, initcall execution, transition from early boot to normal scheduling, rootfs readiness, init memory freeing, and final execution of PID 1.

## Important APIs, Types, And Functions
- `start_kernel()` is the main entry after architecture setup and runs the global initialization sequence.
- `rest_init()` creates the initial userspace-thread wrapper (`kernel_init`) and `kthreadd`, then enters CPU idle.
- `kernel_init()` waits for `kthreadd`, runs `kernel_init_freeable()`, frees init memory, marks kernel text/data read-only, finalizes PTI, and executes init.
- `kernel_init_freeable()` enables normal GFP masks, initializes SMP/workqueues/async/initcalls/KUnit, waits for initramfs, opens console, prepares the root namespace if needed, and loads integrity keys.
- `parse_early_param()`, `unknown_bootoption()`, `setup_boot_config()`, and `setup_command_line()` build the kernel and init argument vectors.
- `do_one_initcall()`, `do_initcall_level()`, and `do_initcalls()` invoke built-in initcall levels with tracing, blacklist handling, and sanity checks.

## Control Flow
Boot begins with interrupts disabled, early CPU and memory structures initialized, bootconfig and command lines prepared, early parameters parsed, and unknown arguments routed to init or environment arrays. `start_kernel()` then initializes allocators, tracing, scheduler, RCU, IRQ/timer/timekeeping/randomness, console, lockdep, namespaces, VFS, cgroups, networking namespaces, and other core subsystems before calling `rest_init()`.

`rest_init()` starts `kernel_init` as PID 1, pins it to the boot CPU until scheduler SMP setup, starts `kthreadd`, changes `system_state` to scheduling, and enters idle. `kernel_init()` performs late boot work, frees init-only memory, switches to `SYSTEM_RUNNING`, and tries init candidates in order: `rdinit`/`/init`, explicit `init=`, `CONFIG_DEFAULT_INIT`, `/sbin/init`, `/etc/init`, `/bin/init`, `/bin/sh`.

## State And Persistence
Global boot state includes `system_state`, `early_boot_irqs_disabled`, command-line buffers, init argv/envp arrays, `execute_command`, `ramdisk_execute_command`, bootconfig data, static key initialization, `reset_devices`, `loops_per_jiffy`, and `rodata_enabled`. It persists `/proc/cmdline` data in `saved_command_line`, exports `system_state`, `reset_devices`, and `static_key_initialized`, and frees init sections after async init work completes.

## Dependencies And Integration Points
This file integrates nearly every core subsystem: architecture setup, memblock, scheduler, workqueues, RCU/SRCU, IRQ/timers/timekeeping, VFS, namespace, cgroup, security, random, ACPI, SMP, KUnit, initramfs, module/initcall infrastructure, tracing, proc/sysfs, and exec. It calls `wait_for_initramfs()` from `initramfs.c` before console/root namespace use.

## Risks And Edge Cases
Ordering is the primary risk. Interrupt state, allocator availability, static keys, security initialization, bootconfig removal from initrd, early parameter parsing, initcall side effects, and async init completion all have strict sequencing. Argument arrays can overflow and panic later. `do_one_initcall()` repairs preemption/IRQ imbalances but reports them. Incorrect initramfs waiting can break `/dev/console` or early userspace discovery.

## Test Signals
Signals include successful system boot, initcall debug traces, KUnit execution from `kunit_run_all_tests()`, bootconfig parse logs, unknown boot option notices, and failure modes such as explicit panic on missing working init. Kernel selftests and platform boot matrices are the real coverage for this file because its behavior spans subsystem ordering.
