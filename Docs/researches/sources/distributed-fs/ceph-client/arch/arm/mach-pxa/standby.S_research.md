# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/standby.S

Purpose: low-level PXA CPU standby path and PXA3 DDR calibration sequence used while entering standby.

Important APIs/types/functions: assembly symbols include `pxa_cpu_standby`, `pm_enter_standby_start`, and `pm_enter_standby_end`. Register constants describe PXA3 DDR controller offsets and calibration bits.

Control flow: `pxa_cpu_standby` executes coprocessor power-mode setup and loops around standby. The standby block programs DDR calibration registers, waits for completion/low-power events, and marks a copyable code region via start/end labels.

State and persistence: mutates CPU power mode and DDR controller calibration/power state. The labeled region is copied/executed by PM code from a safe location.

Dependencies and integration points: used by PXA PM core for standby, with SMEMC/PXA3 memory-controller assumptions.

Risks: pure assembly hardware sequencing with busy waits; incorrect offsets or copy boundaries can deadlock low-power entry.

Test signals: standby entry/exit on PXA targets, DDR stability after wake, and disassembly/link checks for start/end region size.
