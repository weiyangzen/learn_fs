# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcpim.h

## Purpose
`bfa_fcpim.h` defines the HAL FCP initiator module contract used by the BFA core, BFAD driver layer, and FCS FCP initiator bridge. It supplies resource limits, tag mapping macros, state-machine event enums, core runtime structures for FCPIM/ITNIM/IOIM/TSKIM, queue helpers, IO profiling helpers, and public function declarations implemented primarily in `bfa_fcpim.c`.

## Important APIs, Types, And Functions
Important resource constants include `BFA_IO_MAX`, `BFA_FWTIO_MAX`, `BFA_ITNIM_MIN/MAX`, `BFA_IOIM_MIN/MAX`, `BFA_TSKIM_MIN/MAX`, and path-timeout bounds. `BFA_IOIM_IOTAG_MASK`, `BFA_IOIM_RETRY_TAG_OFFSET`, and `BFA_IOIM_RETRY_MAX` define how retry generation bits share the IO tag word. `bfa_ioim_get_index()` maps transfer size into IO profile buckets.

The central structures are `bfa_fcp_mod_s` for the whole FCP module, `bfa_fcpim_s` for initiator-mode state, `bfa_itnim_s` for one initiator-target nexus, `bfa_ioim_s` plus `bfa_ioim_sp_s` for host IOs and slow-path state, and `bfa_tskim_s` for SCSI task management. The header declares the IO, TM, and ITN state-machine event enums and callback prototypes. It also declares LUN mask and throttle APIs, IO profile/stat APIs, attach/ISR functions, and BFAD completion callbacks that lower-layer code invokes.

## Control Flow
The header expresses the module layering. BFA core calls `bfa_fcp_meminfo()`, `bfa_fcp_attach()`, `bfa_fcp_iocdisable()`, and `bfa_fcp_res_recfg()`. FCS or BFAD creates ITNIMs through `bfa_itnim_create()` and drives online/offline/delete events. BFAD allocates IOIMs, starts IOs, and aborts them; firmware completions are dispatched through `bfa_ioim_isr()` and `bfa_ioim_good_comp_isr()`. Task-management allocation/start/free and firmware ISR are similarly exposed. Tag macros convert firmware IO/TM/ITN handles into array objects, keeping the C implementation O(1) for completion dispatch.

## State And Persistence Behavior
The header shows that state is mostly in-memory and list-based: ITNIMs own pending, active, cleanup, task, and delayed-completion queues; IOIMs own SG page queues and callback queue elements; TSKIMs own affected-IO queues and cleanup wait counters. Persistent surfaces are exposed through LUN mask and throttle functions, but the underlying persistent storage lives in the dynamic config module used by `bfa_fcpim.c`. IO profile state is transient but externally queryable while enabled.

## Dependencies And Integration Points
The file includes BFA core, service, firmware message, definition, and common-support headers. It references Linux list primitives and SCSI/FCP protocol types through included driver headers. Its callback declarations are an integration contract with BFAD (`bfa_cb_ioim_*`, `bfa_cb_tskim_done`) and FCS (`bfa_cb_itnim_*`). Macros such as `BFA_FCPIM()`, `BFA_MEM_FCP_KVA()`, `BFA_SNSINFO_FROM_TAG()`, and request-queue helpers are used throughout the FCP implementation and other BFA modules.

## Risks And Edge Cases
The tag mapping macros assume power-of-two or mask-compatible resource counts, valid firmware handles, and stable array layout. `BFA_IOIM_FROM_TAG()` references `fcpim` in the macro body instead of the `_fcpim` parameter, which works only in contexts where a local `fcpim` variable exists and is a maintenance hazard. The retry-bit packing means all code that compares or frees tags must mask generation bits correctly. Structure fields are shared across asynchronous state machines, so callers must respect the lifecycle implied by the events.

## Test Signals
Header-level validation is compile-time and integration-oriented: all users should build with the declared APIs, tag mapping should resolve expected array entries, IO retry tags should increment and mask correctly, and resource reconfiguration should not violate min/max constants. Runtime tests should observe state-machine transitions exposed through these event enums and verify callback contracts are honored by BFAD/FCS implementations.
