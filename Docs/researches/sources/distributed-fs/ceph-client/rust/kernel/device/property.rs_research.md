# sources/distributed-fs/ceph-client/rust/kernel/device/property.rs

## Purpose
`device/property.rs` wraps Linux firmware-node (`fwnode_handle`) APIs for Rust drivers. It provides reference-counted fwnode handles, property reads, child iteration, reference-argument parsing, display formatting, and a guard that distinguishes required and optional properties.

## Important APIs, Types, and Functions
`FwNode` wraps `struct fwnode_handle`. Important methods include `is_of_node`, `display_name`, `property_present`, `property_read_bool`, `property_match_string`, `property_read_array_vec`, `property_count_elem`, `property_read`, `get_child_by_name`, `children`, and `property_get_reference_args`. `NArgs` selects fixed or property-derived argument counts. `FwNodeReferenceArgs` owns returned references. `Property`, `PropertyInt`, and `PropertyGuard` implement typed property reads for strings, integer scalars, fixed arrays, and vectors.

## Control Flow
Property reads call the corresponding C fwnode helper, convert kernel return codes through `to_result`, and wrap the result in `PropertyGuard` when using generic reads. Integer array reads fill `MaybeUninit` buffers and only mark them initialized after successful C calls. Child iteration keeps the previous child in an `ARef`, passes ownership back to `fwnode_get_next_child_node`, and returns a new owned reference each step.

## State and Persistence
`FwNode` state is kernel-managed and refcounted through `fwnode_handle_get` and `fwnode_handle_put`. `FwNodeReferenceArgs` drops the reference embedded in the returned C structure. Property values are copied into Rust-owned scalars, arrays, `KVec`, or `CString`; there is no durable persistence.

## Dependencies and Integration Points
The module is reached from `Device::fwnode()` and integrates with Open Firmware, ACPI, software nodes, `KVec`, `CString`, `ARef`, and device logging via `PropertyGuard::required_by`.

## Risks
The key risks are refcount ownership around child iteration and reference arguments, signed integer reads using unsigned fwnode helpers with layout-compatible storage, and assuming string property lifetime beyond the current copy. Required-property logging can be noisy if used for genuinely optional data.

## Test Signals
Test boolean, string, scalar, fixed-array, vector, and missing-property paths on OF and ACPI backed devices. Iterate child nodes while dropping previous references, parse reference args with fixed and property-provided counts, and verify `required_by` logs only on errors.
