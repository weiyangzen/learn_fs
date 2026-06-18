# sources/distributed-fs/ceph-client/drivers/greybus/manifest.c

## Purpose

`manifest.c` parses Greybus interface manifests. It validates descriptor sizes and types, extracts interface strings/features, creates bundle objects, copies their CPort descriptors, and leaves the interface bundle list ready for control-version negotiation and device registration.

## Important APIs, Types, and Functions

- `gb_manifest_parse()` is the public parser.
- `struct manifest_desc` records descriptor type, payload pointer, size, and list link for the first-pass descriptor index.
- `identify_descriptor()` validates descriptor header, type, minimum size, string padding, and appends descriptors to `intf->manifest_descs`.
- `gb_string_get()` finds a string descriptor by ID, duplicates it with NUL termination, and removes it from the descriptor list.
- `gb_manifest_parse_interface()` handles vendor/product strings, features, and bundle parsing.
- `gb_manifest_parse_bundles()` creates `gb_bundle` objects for non-control bundles.
- `gb_manifest_parse_cports()` validates CPort IDs, rejects control CPort reuse, detects duplicates, allocates bundle CPort descriptors, and removes consumed CPort descriptors.

## Control Flow

Parsing first validates the manifest header size and version. It then walks the descriptor buffer once, creating a list entry for each valid descriptor. It requires exactly one interface descriptor, consumes any referenced strings, records interface features, and then repeatedly consumes bundle descriptors. For each bundle, it ignores legacy control bundles, rejects control-class non-control bundles, creates a bundle object, and copies associated CPort descriptors. Any unconsumed descriptors produce an informational message after a successful parse.

## State and Persistence Behavior

Descriptor list entries are transient and point into the caller-provided manifest buffer. Strings are duplicated into `intf->control`. Bundle objects and copied CPort descriptor arrays persist on `intf->bundles` until interface disable or error cleanup destroys them. `release_manifest_descriptors()` always drains transient descriptors before return.

## Dependencies and Integration Points

The parser depends on Greybus manifest protocol structures, endian helpers, kernel lists/allocation, `gb_bundle_create()` and `gb_bundle_destroy()`, and interface/control fields. `interface.c` provides the manifest buffer fetched over the control connection.

## Risks and Edge Cases

- Descriptor payload pointers reference the original manifest buffer, so no descriptor may outlive parsing.
- Descriptor sizes larger than expected are accepted with a warning for forward compatibility; unknown descriptor types are rejected.
- If a bundle has no valid CPorts, that bundle is destroyed but other bundles can still be accepted.
- Duplicate CPort checks are per bundle temp list; cross-bundle duplicates are not rejected here.
- `gb_string_get()` consumes string descriptors, so repeated use of the same string ID by vendor and product would fail on the second lookup.

## Test Signals

Use synthetic manifests for short headers, size mismatch, too-new versions, each descriptor type minimum size, padded strings, missing or duplicate interface descriptors, missing strings, zero string IDs, legacy control bundle, control class misuse, invalid/duplicate/control CPort IDs, bundle without CPorts, extra descriptors, and cleanup after partial parse failure.
