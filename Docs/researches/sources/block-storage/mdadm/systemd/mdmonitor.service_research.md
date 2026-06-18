# File Research: sources/block-storage/mdadm/systemd/mdmonitor.service

## Purpose
Systemd service for the main mdadm array monitor.

## Behavior
- `DefaultDependencies=no`.
- Runs `BINDIR/mdadm --monitor --scan`.
- Comments document which monitor settings should come from `mdadm.conf` rather than downstream sysconfig files or service flags.

## Integration
Base service that other md check/monitor timers are wanted by.
