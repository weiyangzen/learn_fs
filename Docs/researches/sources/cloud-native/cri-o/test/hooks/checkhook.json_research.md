# sources/cloud-native/cri-o/test/hooks/checkhook.json

## Purpose
OCI hook definition used by integration tests to verify hook execution.

## Important APIs, Types, And Functions
JSON fields define `cmd` regex `.*`, `hook` path `HOOKSDIR/checkhook.sh`, and stage `prestart`.

## Control Flow
Static hook config. CRI-O/hook processing expands or replaces placeholder paths in tests and executes the hook at prestart for matching commands.

## State And Persistence
No state itself. When used, it causes the hook script to append to `HOOKSCHECK`.

## Dependencies And Integration Points
Paired with `checkhook.sh` and `helpers.bash` hook directory setup.

## Risks And Test Signals
Placeholder substitution must be correct or the hook path is invalid. Broad `cmd` matching makes the hook apply to all tested containers.
