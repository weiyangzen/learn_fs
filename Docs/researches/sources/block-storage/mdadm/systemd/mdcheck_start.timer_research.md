# File Research: sources/block-storage/mdadm/systemd/mdcheck_start.timer

## Purpose
Timer for initiating periodic md array scrubbing.

## Behavior
- Runs on the first Sunday of each month at `00:45:00`.
- Installed under `mdmonitor.service`.
- Also enables `mdcheck_continue.timer`.

## Integration
Provides the periodic entry point for scrub scheduling.
