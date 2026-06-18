# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn201/dcn201_resource.h

## Purpose

`dcn201_resource.h` declares the narrow public interface for the DCN 2.0.1 resource pool. It also defines DP PHY power-state constants used by DCN201 code paths.

## Important APIs, Types, And Functions

- `RRDPCS_PHY_DP_TX_PSTATE_POWER_UP`, `HOLD`, `HOLD_OFF`, and `POWER_DOWN` define DP transmitter PHY power-state values.
- `TO_DCN201_RES_POOL()` casts a generic resource pool to `struct dcn201_resource_pool`.
- `struct dcn201_resource_pool` embeds `struct resource_pool base`.
- `dcn201_create_resource_pool()` is the only exported constructor declared here.

## Control Flow

The header has no executable control flow. DC initialization code includes it to construct a DCN201 pool. After construction, behavior is dispatched through the pool's `resource_funcs` table rather than through additional public DCN201-specific declarations.

## State And Persistence Behavior

The header stores no state. The power-state constants are compile-time values. Runtime state is owned by the implementation's pool object, generic DC resource state, and DML state.

## Dependencies And Integration Points

The header includes `core_types.h` and forward-declares `dc`, `resource_pool`, and DML display pipe parameter types. It is intentionally smaller than the DCN20 header because DCN201 reuses most public helpers from `dcn20_resource.h`.

## Risks And Edge Cases

- Callers needing DCN20 helper behavior must include the DCN20 header, not this one.
- The PHY constants must match hardware register encodings; incorrect values can affect DP power transitions.
- The cast macro assumes the embedded `resource_pool base` remains the first/contained member in `struct dcn201_resource_pool`.

## Test Signals

Compile tests catch constructor declaration and type drift. Runtime DCN201 initialization should confirm the constructor is selected for the right ASIC and that DP PHY power handling still uses valid encoded constants where referenced.
