<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.c -->
# sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.c

## Purpose
Implements `OstreeBootconfigParser`, a GObject for parsing, mutating, cloning, and writing Boot Loader Specification style entry files while preserving OSTree-specific boot metadata such as retry counters and overlay initrds.

## Important APIs and Types
The object stores `filename`, separator characters, `tries_left`, `tries_done`, a string-to-string `options` hash table, and `overlay_initrds`. Public APIs include `new`, `clone`, `parse`, `parse_at`, `write`, `write_at`, `set`, `get`, overlay initrd setters/getters, and boot try getters. Private APIs expose the filename and non-standard key variant.

## Control Flow
Parsing reads the file as UTF-8, splits on newlines, accepts lines beginning with an ASCII alpha character, splits each accepted line on space or tab into key/value, stores the first `initrd` in `options`, stores additional `initrd` lines as overlays, parses `+LEFT-DONE` retry counters from the basename, and records the basename. Writing emits standard BLS keys in deterministic order, then overlay initrds, then unknown keys. Clone duplicates options, filename, and overlay initrds.

## State and Persistence
State is in-memory until `write_at()` atomically replaces the target file with `glnx_file_replace_contents_at()`. Unknown/extension keys are preserved in memory and can be serialized through `_ostree_bootconfig_parser_get_extra_keys_variant()`.

## Dependencies and Integration Points
Depends on GLib/GObject, libglnx file helpers, `otutil.h`, and BLS semantics. Bootloader backends read parsed configs from sysroot and use keys such as `title`, `version`, `linux`, `initrd`, `options`, `devicetree`, `fdtdir`, `aboot`, and `abootcfg`.

## Risks
Parser accepts only alpha-starting lines and ignores comments or malformed lines silently. Hash-table iteration makes unknown-key write order nondeterministic. `parse_bootloader_tries()` does not require the counter suffix to end cleanly before extension text. Overlay initrd setting asserts the primary `initrd` already exists.

## Test Signals
Tests should cover standard BLS parse/write, duplicate initrd handling, extension-key preservation, try-counter filenames, malformed lines, deterministic standard key ordering, and staged deployment round trips with custom keys.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-bootconfig-parser.c -->
