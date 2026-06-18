# File Research: sources/block-storage/kvdo/vdo/vdo-component-states.c

This file encodes and decodes the complete component payload stored inside the VDO super block. It defines the current volume format version as `67.0`.

Decode flow:
- `vdo_decode_component_states()` reads and checks the release version against geometry, decodes and validates the volume version, then decodes VDO component data, fixed layout, recovery journal state, slab depot state, and block map state in order.
- On decode failure after layout allocation, it frees the fixed layout.
- `vdo_validate_component_states()` checks the geometry nonce against the superblock nonce and validates the VDO config against physical/logical sizes.

Encode flow:
- `vdo_encode_component_states()` resets the buffer and writes release version, volume version, VDO component, fixed layout, recovery journal, slab depot, and block map states.
- It computes expected encoded size from component helpers and log-only asserts the final payload length matches.

`vdo_destroy_component_states()` currently frees the decoded layout allocation. The file is the glue between component-specific format codecs and the super-block codec.
