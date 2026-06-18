## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml21/src/inc/dml2_internal_shared_types.h

### Purpose
`dml2_internal_shared_types.h` is the central internal contract for DML2. It defines shared data structures and function-pointer interfaces for clock generation, DPM mapping, core mode support/programming, PMO optimization, mcache handling, top-level optimization phases, and the `dml2_instance`.

### Important APIs, Types, And Functions
Major type groups are MCG clock tables and `dml2_mcg_instance`; DPMM map-mode/map-watermark parameter structs and `dml2_dpmm_instance`; core initialization, mode support, mode programming, informative population, mcache allocation, core scratch, and `dml2_core_instance`; optimization-stage state in `display_configuation_with_meta`; PMO parameter structs, strategy masks, PMO scratch/init data, and `dml2_pmo_instance`; top mcache parameter structs; optimization-phase locals and function parameter structs; top callback table `dml2_top_funcs`; and the aggregate `dml2_instance`.

### Control Flow
The header has no executable flow, but its types encode the pipeline: MCG builds a minimum clock table, core checks mode support and produces support info, top optimization phases mutate `display_configuation_with_meta` stage state, PMO callbacks test and optimize targeted power features, DPMM maps mode requirements to SoC DPM states and watermarks, core emits programming, and top callbacks expose the final operations.

### State, Persistence, And Dependencies
All DML2 instance persistence is described here. Long-lived state includes component instances, SoC/IP bounding boxes, minimum clock tables, PMO options, component function tables, and scratch spaces. Per-mode state persists through `display_configuation_with_meta` stages 1 through 5 while optimization proceeds. Dependencies include external library deps, top public types, and core shared types.

### Integration Points
Almost every file in this subset includes this header directly or indirectly. It is the type bridge among factories, SOC15 top, DCN4 FAMS2 PMO, DPMM, MCG, core, and mcache programming code.

### Risks
This header is large and tightly coupled; changing a field can affect many phases. Fixed-size arrays rely on `DML2_MAX_PLANES`, `DML2_MAX_DCN_PIPES`, and PMO constants, so bounds validation belongs at API edges. The misspelled `display_configuation_with_meta` type is pervasive. Some unions reuse scratch memory among phases, so functions must not retain pointers into phase-local union members beyond the call.

### Test Signals
ABI/build tests should cover all component factories against these structs. Behavioral tests should validate stage transitions, scratch reuse, PMO callback tables, mcache parameter mutation, and top function dispatch for each supported project ID.
