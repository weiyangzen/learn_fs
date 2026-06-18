# File Research: sources/block-storage/mdadm/systemd/mdadm-last-resort@.timer

## Purpose
Timer companion for degraded last-resort md activation.

## Behavior
- Waits `OnActiveSec=30`.
- Conflicts with the corresponding block device unit, so the timer is cancelled if the device appears normally.

## Integration
Started by udev incremental assembly rules when mdadm reports an unsafe local start condition.
