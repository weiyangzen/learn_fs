# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_ca.c

## Purpose
This file implements the DVB EN50221 Common Interface adapter for Mantis CAM/CA hardware. It bridges DVB CA callbacks to Mantis host-interface memory/I/O operations, slot reset/status handling, and event-manager lifecycle.

## Important APIs, Types, and Functions
Public functions are `mantis_ca_init` and `mantis_ca_exit`. Internal DVB CA callbacks include attribute memory read/write, CAM control read/write, slot reset, slot shutdown, transport stream control, and slot status polling.

## Control Flow
Initialization allocates `struct mantis_ca`, links it to `struct mantis_pci`, fills the `dvb_ca_en50221` callback table, initializes locks and waitqueues, registers one EN50221 slot with IRQ CAM-change support, and starts the Mantis event manager. Callback reads/writes validate slot 0 and delegate to HIF memory or I/O helpers. Slot reset toggles the PCMCIA reset register, waits, and signals CAM ready. Exit stops the event manager, releases the EN50221 device, and frees state.

## State and Persistence Behavior
The file owns `mantis->mantis_ca`, `ca->en50221`, `ca->ca_lock`, HIF waitqueues, and slot state observed by `mantis_slot_status`. It programs persistent reset state through `MANTIS_PCMCIA_RESET` during slot reset.

## Dependencies and Integration Points
It depends on DVB CA EN50221 core, Mantis HIF/link/register helpers, Mantis event manager, waitqueues, mutexes, and shared `struct mantis_pci` state. Hopper/Mantis IRQ handlers wake CA waitqueues and schedule CA event work.

## Risks
Only slot 0 is supported; callers with other slots receive `-EINVAL`. Error cleanup in init frees `ca` but does not clear `mantis->mantis_ca`, which can leave a stale pointer if later code observes it. Reset timing is fixed and hardware-specific. `mantis_slot_status` trusts event-manager-maintained `slot_state`.

## Test Signals
Insert/remove CAM modules, EN50221 userspace access to attribute and control spaces, slot reset readiness, IRQ CAM-change events, encrypted transport stream enablement, init failure injection, and module unload with active CA users are key signals.
