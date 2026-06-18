<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-instutil.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-instutil.c

## Purpose
Implements the hidden/deprecated `ostree admin instutil` subcommand dispatcher for installer-oriented utilities.

## Important APIs and Types
Static `admin_instutil_subcommands[]` registers `selinux-ensure-labeled` when SELinux is enabled, `set-kargs`, and `grub2-generate`. `ot_admin_builtin_instutil` dispatches to selected subcommands.

## Control Flow
The dispatcher removes the first non-option argument as the subcommand, searches the subcommand table, prints generated help and errors for missing/unknown names, updates `g_prgname`, then invokes the target function with a fresh `OstreeCommandInvocation`.

## State and Persistence
This file only rewrites argv in memory and changes process program name. Persistence belongs to the selected subcommand.

## Dependencies and Integration Points
Uses `OstreeCommand`, admin option parsing, and the instutil builtins header. It is registered under `ostree admin instutil`.

## Risks
In-place argv compaction must preserve options after `--` correctly. Hidden/deprecated commands still affect bootloader, SELinux labels, or kargs through their handlers.

## Test Signals
Dispatcher tests should cover help, unknown subcommands, option passing, `--` behavior, and feature-conditional SELinux command visibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-instutil.c -->
