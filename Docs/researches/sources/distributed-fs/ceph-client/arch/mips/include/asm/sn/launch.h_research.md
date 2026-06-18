<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/launch.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/launch.h

Purpose: Defines the SGI SN PROM launch structure and PROM entry-point wrappers for starting and managing slave CPUs.

Important APIs/types/functions: `LAUNCH_MAGIC`, struct offsets, launch states, `launch_state_t`, `launch_proc_t`, `launch_t`, and function-pointer macros `LAUNCH_SLAVE`, `LAUNCH_WAIT`, `LAUNCH_POLL`, `LAUNCH_LOOP`, `LAUNCH_FLASH`.

Control flow: The kernel fills per-CPU launch records with function, call parameter, stack, GP, and exception vector addresses, invokes PROM launch/wait/poll entry points, and secondary CPUs report state through the busy/state fields.

State and persistence: State is per-NASID/per-slice launch memory from KLDIR plus PROM entry points at fixed addresses. Fields are shared between PROM, boot CPU, and slave CPU.

Dependencies and integration points: Depends on SN types/address macros and SN0 PROM address constants. Integrated by IP27 SMP bring-up and PROM interaction code.

Risks: The structure has fixed offsets used by low-level code. Bad stack/GP/vector values or wrong NASID/slice can hang secondary boot.

Test signals: SN SMP secondary CPU boot, PROM launch wait/poll paths, and CPU hotplug/diagnostic launch tests are relevant.

Source read size: 106 lines, 3420 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/sn/launch.h -->
