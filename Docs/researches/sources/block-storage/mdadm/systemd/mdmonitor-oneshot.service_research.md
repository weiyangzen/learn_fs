# File Research: sources/block-storage/mdadm/systemd/mdmonitor-oneshot.service

## Purpose
One-shot reminder service for degraded md arrays.

## Behavior
- Sets default `MDADM_MONITOR_ARGS=--scan`.
- Optionally reads `/run/sysconfig/mdadm`.
- Runs optional environment preparation script.
- Executes `BINDIR/mdadm --monitor --oneshot $MDADM_MONITOR_ARGS`.

## Integration
Scheduled by `mdmonitor-oneshot.timer` and associated with `mdmonitor.service`.
