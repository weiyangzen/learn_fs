# sources/distributed-fs/ceph-client/kernel/power/poweroff.c

## Purpose
Registers the SysRq `o` handler that requests a graceful kernel poweroff. It is a small bridge from emergency keyboard/sysrq handling into the normal reboot/power-management poweroff path.

## Important APIs, Types, and Functions
`do_poweroff()` is a workqueue callback that calls `kernel_power_off()`. `handle_poweroff()` schedules that work on the first online CPU with `schedule_work_on(cpumask_first(cpu_online_mask), &poweroff_work)`. `sysrq_poweroff_op` describes the SysRq key operation, help text, action text, and `SYSRQ_ENABLE_BOOT` enable mask. `pm_sysrq_init()` registers key `o` with `register_sysrq_key()` as a `subsys_initcall`.

## Control Flow
When SysRq `o` is triggered, the sysrq layer calls `handle_poweroff()`. The handler does not power off directly from sysrq context; it schedules `poweroff_work` on the boot/first online CPU. The workqueue callback then invokes `kernel_power_off()`, allowing the existing kernel poweroff path to run in process context.

## State and Persistence Behavior
The only state is the statically declared work item and key operation. There is no persistent configuration or sysfs state. Registration lasts for the boot lifetime once the initcall succeeds.

## Dependencies and Integration Points
The file depends on sysrq, reboot/poweroff, workqueue, CPU mask, and initcall infrastructure. It integrates with the global sysrq key registry and the generic `kernel_power_off()` path, including architecture and platform poweroff handlers.

## Risks
Risks are limited but include scheduling on an invalid CPU mask if called during severe CPU-hotplug failure, assuming workqueue execution is still possible during an emergency, and interactions with platform poweroff handlers that may sleep or fail. Because it uses `SYSRQ_ENABLE_BOOT`, policy around sysrq enable masks controls exposure.

## Test Signals
Enable sysrq and issue SysRq `o` on a test machine or VM, then verify `kernel_power_off()` is reached and no direct sysrq-context sleeping occurs. Build coverage should include sysrq-enabled kernels and CPU hotplug configurations.
