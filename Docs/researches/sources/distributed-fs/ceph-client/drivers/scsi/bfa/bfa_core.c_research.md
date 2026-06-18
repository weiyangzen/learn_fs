# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_core.c

## Purpose
`bfa_core.c` implements the BFA HAL core for Fibre Channel adapters. It wires firmware interrupt dispatch tables, common tracing, IOCFC lifecycle state machines, DMA memory claiming, interrupt processing, firmware configuration handshakes, Fabric Assigned Address query handling, attach/detach, completion callback processing, and default resource configuration.

## Important APIs and Functions
The file defines ISR dispatch arrays `bfa_isrs` for BFI message classes and `bfa_mbox_isrs` for mailbox classes. Public entry points include `bfa_iocfc_meminfo`, `bfa_iocfc_attach`, `bfa_iocfc_init`, `bfa_iocfc_start`, `bfa_iocfc_stop`, `bfa_iocfc_isr`, `bfa_iocfc_get_attr`, `bfa_iocfc_israttr_set`, `bfa_iocfc_set_snsbase`, `bfa_iocfc_enable`, `bfa_iocfc_disable`, `bfa_iocfc_is_operational`, `bfa_iocfc_get_bootwwns`, `bfa_iocfc_get_pbc_vports`, `bfa_cfg_get_meminfo`, `bfa_attach`, `bfa_detach`, `bfa_comp_deq`, `bfa_comp_process`, `bfa_comp_free`, and `bfa_cfg_get_default`. Internal helpers attach common modules, initialize chip-specific hardware callbacks, claim DMA memory, configure queue registers, process firmware config responses, and start or disable submodules.

## Control Flow and State
The IOCFC FSM moves from `stopped` to `initing`, reads dynamic config, sends firmware config, queues the init callback, then waits for `START` to become `operational`. Operational entry initializes the FC port, starts submodules, enables queue processing, acknowledges response queues, and refreshes LUN mask runtime state. Stop paths write dynamic config, disable IOC, disable ISR handling, quiesce submodules, and queue completion. Enable/disable paths reuse IOC callbacks and optionally queue driver completions. Failure paths disable interrupts and submodules, then either wait for recovery or callback with failure.

## Interrupt and Queue Behavior
`bfa_intx` and `bfa_msix_all` read interrupt status, acknowledge queue causes, drain response queues with `bfa_isr_rspq`, resume request waiters with `bfa_reqq_resume`, and route error/mailbox interrupts through `bfa_msix_lpu_err`. Response queue messages are dispatched by message class, with unknown classes warning and stopping trace capture.

## State and Persistence Behavior
Persistent and firmware-derived state enters through the config response page. `bfa_iocfc_cfgrsp` converts firmware resource counts from big endian, installs queue register offsets, reconfigures resources, installs MSI-X queue handlers, and completes config only after PBC WWNs or FAA address messages are available. Boot WWNs and PBC vports are read from `cfgrsp`; no disk persistence is performed.

## Dependencies and Integration Points
The file integrates almost every BFA submodule: port, FCXP, LPS, UF, rport, FCP, task management, diagnostics, SFP, flash, PHY, FRU, CEE, adapter block, dynamic config, IOC, mailbox, and PCI register code. Firmware contracts come through `bfi_iocfc_*` messages and register offsets.

## Risks and Test Signals
Risk centers on asynchronous FSM events racing stop/disable/failure, queue processing during interrupt disable, firmware config endian handling, callback queue lifetime, and assuming power-of-two queue sizes. Test with init/start/stop, IOC failure during each FSM state, MSI-X and INTx interrupts, firmware config with reduced resources, FAA supported/unsupported paths, boot PBC extraction, and request queue exhaustion/resume.
