<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtins.h -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtins.h

## Purpose
Declares installer utility subcommand handlers for `ostree admin instutil`.

## Important APIs and Types
Declares SELinux relabel, set-kargs, and grub2-generate handlers with the standard `OstreeCommandInvocation` signature.

## Control Flow
No runtime logic is implemented.

## State and Persistence
No state is stored in the header; declared commands may mutate labels, bootloader config, and deployment kargs.

## Dependencies and Integration Points
Includes `ot-main.h` and is consumed by the instutil dispatcher and implementation files.

## Risks
Feature guards in the dispatcher must stay aligned with available declarations/definitions, especially SELinux.

## Test Signals
Feature-matrix compilation and dispatcher link tests cover this header.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtins.h -->
