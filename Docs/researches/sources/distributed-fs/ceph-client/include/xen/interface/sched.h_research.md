# sources/distributed-fs/ceph-client/include/xen/interface/sched.h

## Purpose
`sched.h` defines Xen scheduler-operation ABI commands for guest yield/block/shutdown, event-channel polling, remote shutdown, shutdown-code latching, domain watchdogs, and dom0 pin override.

## Important APIs, Types, and Functions
Important commands are `SCHEDOP_yield`, `block`, `shutdown`, `poll`, `remote_shutdown`, `shutdown_code`, `watchdog`, and `pin_override`. Payloads include `sched_shutdown`, `sched_poll`, `sched_remote_shutdown`, `sched_watchdog`, and `sched_pin_override`. Shutdown reasons include poweroff, reboot, suspend, crash, watchdog, and soft reset.

## Control Flow
Guests call `HYPERVISOR_sched_op`. Blocking atomically unmasks event delivery when needed, poll waits for event-channel ports or a timeout, shutdown notifies control software, and watchdog setup/poke/destroy changes hypervisor timers. Suspend has special x86 PV calling conventions for start-info MFN.

## State and Persistence Behavior
Scheduler state is runtime hypervisor state: VCPU runnable/block status, pending shutdown reason, watchdog timer, and optional pin override. Shutdown reason is visible to control tooling until acted on.

## Dependencies and Integration Points
It depends on event-channel port types and Xen base domain types. Linux Xen time/event-channel, suspend/resume, panic/reboot, and watchdog paths use this ABI.

## Risks and Test Signals
Risks include wakeup-wait races if blocking is not used correctly, wrong suspend return interpretation, remote shutdown misuse, watchdog accidentally terminating a domain, and pin override privilege failures. Test signals include event-channel poll/block tests, reboot/poweroff/suspend flows, watchdog expiry/poke/destroy, and soft-reset handling.
