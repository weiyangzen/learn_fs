# File Research: sources/block-storage/lvm2/lib/properties/prop_common.h

This header defines common property infrastructure and report-field-to-property macros.

Content:
- `struct lvm_property_type` with type mask, id, flags for settable/string/integer/signed, value union, getter, setter.
- Prototypes for generic get/set and not-implemented handlers.
- Macros to generate numeric, signed numeric, and string property getter/setter functions.
- Field type constants: `STR`, `NUM`, `BIN`, `SIZ`, `PCT`, `TIM`, `SNUM`, `STR_LIST`.
- `FIELD_MODIFIABLE`.
- `FIELD(...)` macro that maps report field definitions into property descriptors.

Role:
- Bridges report column definitions and property API machinery.

Risks:
- Heavy macro use means field definitions must match expected naming conventions for `_id_get` and `_id_set`.
- `FIELD` encodes string/integer/signed flags from field type; adding a new field type requires updating this mapping.
