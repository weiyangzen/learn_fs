# File Research: sources/block-storage/mdadm/systemd/mdcheck_continue.timer

## Purpose
Timer for continuing md scrub/check operations.

## Behavior
- Runs daily at `1:00:00`.
- Installed as wanted by `mdmonitor.service`.

## Integration
Complements `mdcheck_start.timer`, allowing long checks to resume in bounded windows.
