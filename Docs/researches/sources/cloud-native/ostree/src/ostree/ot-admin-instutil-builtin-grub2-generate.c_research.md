<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-grub2-generate.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-grub2-generate.c

## Purpose
Implements `ostree admin instutil grub2-generate`, generating GRUB2 configuration for a selected bootversion.

## Important APIs and Types
Exports `ot_admin_instutil_builtin_grub2_generate`; calls `ostree_cmd__private__()->ostree_generate_grub2_config`.

## Control Flow
The command parses superuser/unlocked admin context, accepts an optional bootversion argument or reads `_OSTREE_GRUB2_BOOTVERSION` or current sysroot bootversion, validates it is 0 or 1, and delegates config generation with deployment count limit 1.

## State and Persistence
Writes GRUB2 boot configuration through the private command API.

## Dependencies and Integration Points
Depends on sysroot bootversion state, environment override, and private bootloader generation code. Used by installer/bootloader workflows.

## Risks
Invalid environment values are not explicitly rejected before the final assertion path if not 0/1. Bootversion determines which boot tree is generated, so mismatches can affect bootability.

## Test Signals
Tests should cover explicit bootversion 0/1, invalid values, environment override, default sysroot bootversion, and generated GRUB output.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-instutil-builtin-grub2-generate.c -->
