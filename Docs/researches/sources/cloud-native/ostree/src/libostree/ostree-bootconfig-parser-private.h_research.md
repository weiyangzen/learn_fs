<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser-private.h

## Purpose
Declares private helpers for retrieving bootconfig parser internals not exposed in the public header.

## Important APIs and Types
`_ostree_bootconfig_parser_filename()` returns the parsed basename. `_ostree_bootconfig_parser_get_extra_keys_variant()` returns non-standard bootloader keys as a `GVariant` dictionary.

## Control Flow
No runtime flow is present in the header.

## State and Persistence
The helpers expose already parsed in-memory parser state. Extra keys can be serialized by deployment code to preserve consumer extensions.

## Dependencies and Integration Points
Includes `ostree-bootconfig-parser.h`. Used by sysroot/deployment internals that need filename metadata or extension-key preservation during staged deployment serialization.

## Risks
The filename pointer is transfer-none and tied to parser lifetime. The extra-key filter must stay synchronized with standard BLS keys in the implementation.

## Test Signals
Tests should parse files with custom keys, call the private variant helper through internal code, and confirm standard keys are excluded while extension keys survive round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser-private.h -->
