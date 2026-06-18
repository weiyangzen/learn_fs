# File Research: sources/block-storage/mdadm/systemd/mdcheck_continue.service

## Purpose
Systemd service for continuing md array scrubbing/check work.

## Behavior
- Sets `MDADM_CHECK_DURATION=6 hours`.
- Runs `MISCDIR/mdcheck --start --duration ${MDADM_CHECK_DURATION}`.
- Comment explains that `--start` continues existing checks or starts from zero if no marker exists.

## Integration
Used with `mdcheck_continue.timer` and wanted by `mdmonitor.service`.
