# sources/distributed-fs/ceph-client/arch/sparc/kernel/hvcalls.S

## Purpose
`hvcalls.S` provides assembly wrappers around sun4v hypervisor fast and core trap calls. It exposes the low-level ABI used by IRQ, CPU, MMU, LDC, console, service-channel, performance, reboot, and DAX/CCB code.

## Important APIs, Types, and Functions
Wrappers include interrupt functions (`sun4v_devino_to_sysino`, `sun4v_intr_*`, `sun4v_vintr_*`), CPU functions (`sun4v_cpu_*`), MMU functions, version negotiation, TOD/console/machine state, LDC queue/map/copy calls, service channel calls, MMU statistics, performance-register calls for Niagara/N2/VT/T5/M7, reboot data, and CCB functions. Several symbols are exported, including watchdog/perf/CCB helpers.

## Control Flow and State
Most wrappers place the HV function number in `%o5`, execute `ta HV_FAST_TRAP` or `ta HV_CORE_TRAP`, store out-parameters from `%o1`/`%o2`/`%o3` into caller-provided pointers, and return `%o0` status. Some wrappers translate results, such as `sun4v_cpu_state()` returning negative status or state, and console read mapping break/hup pseudo-results. Service send/recv use a register window because they need more stable argument preservation.

## Persistence and Dependencies
The file mutates no kernel data directly except caller-provided out-parameters. It depends completely on the sun4v hypervisor ABI, constants in `<asm/hypervisor.h>`, CCB offsets, and SPARC calling convention.

## Integration Points, Risks, and Test Signals
Integration is foundational for sun4v boot, IRQ, LDC/VIO, domain services, CPU hotplug, console, performance counters, and reboot. Risks include mismatched out-parameter registers, ABI drift across hypervisor versions, missing error handling in callers, and a suspicious `sun4v_ccb_submit()` dependence on `%o4/%o5` pointer conventions. Test signals are HVAPI negotiation, CPU start/stop, interrupt enable/EOI, LDC traffic, console I/O, reboot data setting, and CCB submit/info/kill status on capable hardware.
