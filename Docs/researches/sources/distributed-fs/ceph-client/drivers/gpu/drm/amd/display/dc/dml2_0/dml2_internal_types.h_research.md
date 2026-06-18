## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml2_0/dml2_internal_types.h

### Purpose
`dml2_internal_types.h` defines wrapper-side DML2 context, scratch, mapping, and architecture types used by DC integration code.

### Important APIs, Types, And Functions
Key structs include `dml2_wrapper_optimize_configuration_params`, scratch structs for lowest-state and RQ/DLG calculations, `dml2_dml_to_dc_pipe_mapping`, `dml2_wrapper_scratch`, `dml2_helper_det_policy_scratch`, `dml21_wrapper_scratch`, `dml2_pipe_combine_factor`, `dml2_pipe_combine_scratch`, and the aggregate `dml2_context`. It also defines `__DML2_WRAPPER_MAX_STREAMS_PLANES__` and `enum dml2_architecture`.

### Control Flow
There is no executable flow. The structures describe how wrapper code carries current/new display configs, policies, mode-support data, flexible pipe mapping state, plane duplicate tracking, HPO encoder mapping, DML2.0 state, and DML2.1 top-interface state.

### State, Persistence, And Dependencies
`struct dml2_context` persists architecture selection, configuration callbacks/options, DET helper scratch, pipe-combine scratch, and a union of DML2.0 and DML2.1 state. Dependencies include DC types, legacy display mode core, wrapper and policy headers, DML2.1 top interfaces, and public DML top types.

### Integration Points
`dml2_dc_resource_mgmt.c` uses these types to choose DML2.0 versus DML2.1 mapping behavior, to access mapping arrays, to detect plane duplicates, and to store source/target pipe combine factors.

### Risks
The mapping arrays are limited to six stream/plane entries, so larger configurations need validation before use. The union means DML2.0 and DML2.1 state cannot be live simultaneously in one context. Mapping validity booleans must be maintained consistently; lookup helpers assert and return sentinel indexes when entries are missing.

### Test Signals
Tests should cover mapping-table population for streams, planes, DML pipe indexes, duplicate planes, DML2.0 and DML2.1 architecture selection, and pipe-combine scratch reset between mapping operations.
