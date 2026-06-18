# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css_sp.h

## Purpose
Declares the public host-side SP control and pipeline-staging interface for AtomISP CSS.

## Important APIs, Types, and Functions
Exports initialization/store calls (`sh_css_sp_store_init_dmem()`, `store_sp_stage_data()`, `store_sp_group_data()`), pipeline setup/teardown (`sh_css_sp_init_pipeline()`, `sh_css_sp_uninit_pipeline()`), copy start/status helpers, host2sp command and frame update routines, event IRQ mask initialization, SP running/start APIs, input formatter/circuit configuration, raw-pool and ISYS event toggles, DMA debug-mask functions, and global staging structs.

## Control Flow
Consumers include this header to build SP pipeline data before starting firmware, update dynamic frame slots while streaming, and control SP execution. The implementation in `sh_css_sp.c` performs the actual DDR/DMEM writes.

## State and Persistence Behavior
The exported globals expose shared mutable SP/ISP staging state. Callers must treat them as current pipeline-construction state rather than independent objects.

## Dependencies and Integration Points
Includes `system_global.h`, `type_support.h`, input formatter config, binary types, CSS public types, and pipeline definitions. It integrates with CSS pipeline creation, firmware boot, event handling, and debug paths.

## Risks
The broad API surface makes ordering important: stages must be initialized before stored, host2sp commands require firmware readiness, and dynamic frame updates must stay within fixed firmware arrays. Direct global access increases risk of stale or concurrent mutation.

## Test Signals
Compile coverage from pipeline, stream, and firmware-control units plus runtime checks for all declared update functions are the main signals.
