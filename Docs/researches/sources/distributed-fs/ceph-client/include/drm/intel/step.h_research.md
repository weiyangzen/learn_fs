# sources/distributed-fs/ceph-client/include/drm/intel/step.h

Purpose: defines a common symbolic Intel stepping enumeration for display and GT code.

Important APIs/types/functions: `STEP_NAME_LIST(func)` enumerates A0 through J3 by applying a callback macro. `STEP_ENUM_VAL(name)` maps names to `STEP_name`. `enum intel_step` includes `STEP_NONE`, all generated step names, `STEP_FUTURE`, and `STEP_FOREVER`.

Control flow: no runtime logic. Other code can reuse `STEP_NAME_LIST` to generate string tables, comparisons, or switch cases consistently.

State and persistence: none. The enum values are symbolic software compatibility markers and may not map directly to hardware encodings.

Dependencies and integration: standalone macro/enum header. Integrated by Intel platform stepping tables, workarounds, and display/GT feature gating.

Risks and test signals: ordering is part of comparison semantics; inserting values in the wrong place can change workaround ranges. Test platform stepping decode, workaround table boundaries, and compile-time generation of any parallel name arrays.
