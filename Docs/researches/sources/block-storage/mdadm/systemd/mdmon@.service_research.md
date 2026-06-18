# File Research: sources/block-storage/mdadm/systemd/mdmon@.service

## Purpose
Systemd template service for running `mdmon` metadata monitor for an external metadata container.

## Behavior
- `DefaultDependencies=no`.
- Runs before `initrd-switch-root.target`.
- Uses `IgnoreOnIsolate=true`.
- Executes `BINDIR/mdmon --foreground --offroot --takeover %I`.
- Uses `Slice=system.slice` to avoid early shutdown conflicts.

## Integration
Triggered by udev rules for arrays with external containers, including initrd-prefixed instances.
