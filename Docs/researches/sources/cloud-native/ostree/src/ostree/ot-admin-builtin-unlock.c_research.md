<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-unlock.c -->
# sources/cloud-native/ostree/src/ostree/ot-admin-builtin-unlock.c

## Purpose
Implements `ostree admin unlock`, making the booted deployment mutable through development, hotfix, or transient overlay modes.

## Important APIs and Types
Exports `ot_admin_builtin_unlock`. Options `--hotfix` and `--transient` select `OstreeDeploymentUnlockedState`; default is development.

## Control Flow
The command parses superuser context, rejects extra args, requires a booted deployment, rejects simultaneous hotfix and transient, calls `ostree_sysroot_deployment_unlock`, and prints mode-specific instructions.

## State and Persistence
Mutates booted deployment unlocked state and mounts/prepares overlayfs behavior through sysroot APIs. Hotfix mode creates a non-hotfixed rollback target.

## Dependencies and Integration Points
Integrates with deployment metadata, overlayfs/unlocked deployment handling, and status display of unlocked state.

## Risks
Unlocking intentionally weakens immutability. Hotfix state persists differently from development/transient modes. Correct rollback creation is delegated to sysroot APIs.

## Test Signals
Tests should cover all modes, conflict validation, no booted deployment, status output after unlock, reboot persistence/discard behavior, and rollback creation in hotfix mode.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/ostree/ot-admin-builtin-unlock.c -->
