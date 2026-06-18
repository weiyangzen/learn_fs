# File Research: sources/block-storage/mdadm/systemd/mdcheck_start.service

## Purpose
Systemd service that starts or restarts md array scrubbing.

## Behavior
- Wants `mdcheck_continue.timer`.
- Runs `MISCDIR/mdcheck --restart`.

## Integration
Scheduled by `mdcheck_start.timer`, with continuation delegated to the continuation timer/service.
