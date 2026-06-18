# File Research: sources/block-storage/mdadm/udev-md-raid-assembly.rules

## Purpose
udev rules for incremental md array assembly from component-device events.

## Behavior
- Skips anaconda contexts and non-block devices.
- Handles `linux_raid_member`, `ddf_raid_member`, and IMSM members unless blocked by kernel command-line flags.
- Avoids premature handling of md/dm change events.
- Runs `mdadm --incremental --export ... --offroot`.
- Starts degraded last-resort timer for unsafe local arrays.
- On remove events, runs `mdadm -If` with optional path information.

## Integration
Primary automatic assembly hook for udev-discovered RAID members.
