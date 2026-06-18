# File Research: sources/block-storage/kvdo/vdo/vdo-component.c

This file handles the VDO component portion of super-block component data. The current component-data format version is `41.0`.

Encoding/decoding:
- Defines packed little-endian `packed_vdo_config` and `packed_vdo_component_41_0`.
- `vdo_get_component_encoded_size()` returns version header plus packed component size.
- `vdo_encode_component()` writes the component-data version and packed state.
- `vdo_decode_component()` reads and validates version, then decodes format `41.0`.

`vdo_validate_config()` enforces configuration constraints:
- slab size must be nonzero, power of two, and within maximum slab bits;
- slab journal blocks must meet minimum and not exceed slab size;
- derived slab config must contain at least one data block;
- physical blocks must be nonzero, within maximum, and equal the supplied physical size;
- logical blocks, when externally specified, must match and be within maximum;
- recovery journal size must be nonzero and power of two.

Errors are returned as assertions/status codes, with physical/logical mismatches logged and reported as `VDO_PARAMETER_MISMATCH`.
