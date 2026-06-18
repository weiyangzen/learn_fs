# sources/distributed-fs/ceph-client/arch/arm/mach-at91/sama7.c

Purpose: registers the `sama7` AT91/Microchip device-tree machine descriptor.

Important APIs/types/functions: a compatible string table selects the SoC family and a `DT_MACHINE_START` block wires optional `.init_machine` PM initialization plus `.dt_compat` matching.

Control flow: during early ARM machine selection, the kernel matches the root DT compatible, then runs the descriptor's init hook to initialize PM or platform devices.

State and persistence: no local mutable state beyond descriptor registration; PM init may populate shared AT91 PM state.

Dependencies and integration: depends on AT91 `generic.h` init declarations, DT root compatible strings, and the ARM machine descriptor framework.

Risks: wrong compatible strings prevent the platform from matching or skip required PM initialization.

Test signals: boot with matching DT compatible, machine descriptor selection, and PM init messages for configured suspend support.
