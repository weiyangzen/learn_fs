# File Research: sources/block-storage/mdadm/systemd/mdadm-grow-continue@.service

## Purpose
Systemd template service for continuing an md reshape/grow operation on `/dev/%I`.

## Behavior
- `DefaultDependencies=no`.
- Runs `BINDIR/mdadm --grow --continue /dev/%I`.
- Suppresses standard input, output, and error.

## Integration
Referenced by mdadm/udev/systemd flows when an array has active reshape metadata and continuation should be delegated to systemd.
