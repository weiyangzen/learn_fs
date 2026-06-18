# File Research: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.timer

## Purpose
Timer for periodic degraded-array reminder checks.

## Behavior
- Runs daily at `2:00:00`.
- Installed as wanted by `mdmonitor.service`.

## Integration
Triggers `mdmonitor-oneshot.service`.
