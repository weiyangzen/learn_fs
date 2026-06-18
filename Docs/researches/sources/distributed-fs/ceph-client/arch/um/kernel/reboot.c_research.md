# sources/distributed-fs/ceph-client/arch/um/kernel/reboot.c

## Purpose
Provides UML machine restart, halt, poweroff, and cleanup behavior. It terminates userspace address-space helper processes, runs UML exit hooks, and routes restart/poweroff into SKAS longjmp exits.

## Important APIs, Types, and Functions
Exports `pm_power_off`. `uml_cleanup()` disables normal allocation, runs `do_uml_exitcalls()`, and kills all process-backed UML address spaces. `machine_restart()`, `machine_power_off()`, and `machine_halt()` are the architecture machine control hooks. `register_power_off()` installs a generic `sys_off` poweroff handler.

## Control Flow, State, and Persistence
`kill_off_processes()` walks the task list under `tasklist_lock`, finds tasks with an mm, extracts the host pid from `mm->context.id.pid`, and kills/reaps the ptraced process. No data persists after shutdown; the goal is process and host resource cleanup.

## Dependencies and Integration Points
Uses scheduler task iteration, `find_lock_task_mm()`, UML `os_kill_ptraced_process()`, SKAS `reboot_skas()`/`halt_skas()`, and sys-off registration. It is invoked by panic/exit/reboot paths and by `main.c` during host-process teardown.

## Risks and Test Signals
Risks are tasklist races, stale/invalid child pids, and exitcall ordering. Test reboot, halt, poweroff, panic, and failed boot exits; watch for leaked `uml-userspace` processes, unreaped children, and repeated poweroff callbacks.
