# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.h

## Purpose

`dc_spl_filters.h` declares common SSPL filter helper definitions.

## Important APIs, Types, And Functions

- `NUM_PHASES_COEFF 33`: number of coefficient phases used by the helper.
- Declares `SPL_NAMESPACE(convert_filter_s1_10_to_s1_12(...))`.
- Includes `dc_spl_types.h`.

## Control Flow

No executable control flow is present.

## State And Persistence Behavior

The header stores no state. The declared helper writes caller-owned buffers.

## Dependencies And Integration Points

It is included by `dc_spl_filters.c` and by iSHARP filter code. The phase count must align with static filter table lengths across SSPL.

## Risks And Edge Cases

If `NUM_PHASES_COEFF` changes without regenerating static coefficient tables, conversion lengths and table sizes will diverge. Consumers must provide correctly sized buffers.

## Test Signals

Build coverage validates declarations. Filter conversion tests should verify the phase-count contract against all tap counts used by scaler and iSHARP tables.
