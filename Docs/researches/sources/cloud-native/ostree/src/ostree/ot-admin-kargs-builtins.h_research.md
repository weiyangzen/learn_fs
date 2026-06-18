<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtins.h

## Purpose
Declares admin kargs subcommand handlers.

## Important APIs and Types
Defines `BUILTINPROTO` for `ot_admin_kargs_builtin_edit_in_place` using the standard command signature.

## Control Flow
No implementation logic exists.

## State and Persistence
No state is stored in the header. The declared handler mutates deployment kargs.

## Dependencies and Integration Points
Includes `ot-main.h`; consumed by the kargs dispatcher and edit-in-place implementation.

## Risks
Prototype and dispatcher table must remain aligned.

## Test Signals
Compile/link tests and kargs dispatcher tests cover this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-kargs-builtins.h -->
