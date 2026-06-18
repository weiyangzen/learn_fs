# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/sspl/dc_spl_filters.c

## Purpose

`dc_spl_filters.c` provides a small filter coefficient format conversion helper for SPL scaler tables.

## Important APIs, Types, And Functions

- `SPL_NAMESPACE(convert_filter_s1_10_to_s1_12(const uint16_t *s1_10_filter, uint16_t *s1_12_filter, int num_taps))`: converts fixed-point coefficients from S1.10 to S1.12 by multiplying each entry by four.
- Uses `NUM_PHASES_COEFF` from the paired header to determine `33 * num_taps` entries.

## Control Flow

The function computes `num_entries = NUM_PHASES_COEFF * num_taps`, then linearly copies and scales every coefficient from source to destination.

## State And Persistence Behavior

No persistent state exists. The destination buffer is caller-owned and overwritten in place.

## Dependencies And Integration Points

It includes `dc_spl_filters.h` and is linked into the SSPL component. It supports filter-table preparation for scaler/EASF/iSHARP code that needs S1.12 hardware coefficient format from S1.10 source tables.

## Risks And Edge Cases

- The function assumes both pointers are valid and the destination has enough space.
- Multiplying by four can overflow if a coefficient is not a valid S1.10 value fitting the expected hardware range.
- `num_taps` must match the table layout used by the caller.

## Test Signals

Unit tests can convert known 3/4/6/8-tap arrays and verify every output equals input times four for exactly `33 * taps` entries. Memory sanitizer coverage catches undersized buffers.
