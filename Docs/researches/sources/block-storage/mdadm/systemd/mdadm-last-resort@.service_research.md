# File Research: sources/block-storage/mdadm/systemd/mdadm-last-resort@.service

## Purpose
One-shot systemd service that activates a degraded md array after a delay when safer assembly did not complete.

## Behavior
- Runs only if `/sys/devices/virtual/block/%i/md/sync_action` does not exist.
- Executes `BINDIR/mdadm --run /dev/%i`.

## Integration
Paired with `mdadm-last-resort@.timer` and triggered by udev assembly rules for unsafe-but-local arrays.
