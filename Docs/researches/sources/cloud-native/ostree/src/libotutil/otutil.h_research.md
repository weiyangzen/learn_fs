<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/otutil.h -->
# sources/cloud-native/ostree/src/libotutil/otutil.h

## Purpose
Acts as the umbrella include for OSTree utility helpers and common inline macros used across command and library code.

## Important APIs and Types
Defines `OT_VARIANT_BUILDER_INITIALIZER` compatibility for older GLib, `ot_booltostr`, `ot_gobject_refz`, `ot_transfer_out_value`, journald wrapper macros, and `GMainContextPopDefault` autoptr cleanup helpers. It includes checksum, fd, filesystem, keyfile, option, tool, Unix, variant-builder, and variant-utils headers, plus GPG helpers when enabled.

## Control Flow
Inline logic is limited to simple conversions, nullable ref, output-value transfer, journald no-op wrappers, and thread-default main-context push/pop helpers.

## State and Persistence
No durable state is stored. `_ostree_main_context_new_default` creates a new `GMainContext` and makes it thread-default until autoptr cleanup pops and unrefs it.

## Dependencies and Integration Points
Depends on GLib/GIO, libglnx, syslog, optional systemd journal APIs, and many local libotutil headers. Most CLI and helper sources include this file to get a consistent internal utility environment.

## Risks
Because it is an umbrella header, changes can have broad rebuild and namespace effects. The GLib-version initializer must remain aligned with GLib's struct shape. Journald macros intentionally compile to no-ops without systemd, so callers must not rely on side effects in arguments.

## Test Signals
Full-tree compilation across GLib/systemd/GPG feature combinations and small tests for thread-default main-context cleanup are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libotutil/otutil.h -->
