<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.h -->
# sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.h

## Purpose
Declares the public `OstreeBootconfigParser` GObject API.

## Important APIs and Types
Defines `OSTREE_TYPE_BOOTCONFIG_PARSER`, cast/check macros, opaque `OstreeBootconfigParser`, type getter, constructor, clone, parse/write APIs for `GFile` and fd-relative paths, key setters/getters, overlay initrd setters/getters, and boot try getters.

## Control Flow
No implementation flow; the header defines callable API and ownership conventions.

## State and Persistence
The parser owns bootconfig key/value state and writes it back to files through the implementation.

## Dependencies and Integration Points
Includes `<gio/gio.h>` and is consumed by sysroot deployment code plus bootloader backends.

## Risks
Callers receive transfer-none strings and string vectors from getters. Because parsing is single-use on a fresh parser in the implementation, callers should not reparse into an initialized instance.

## Test Signals
ABI compilation, GObject type checks, introspection expectations, and behavior tests for the implementation validate this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.h -->
