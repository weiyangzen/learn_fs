# File Research: sources/block-storage/mdadm/misc/mdcheck

## Role

`misc/mdcheck` is a Bash helper intended for periodic systemd/cron execution to run md array consistency checks with optional time budgeting and checkpointing.

## Modes

- `--continue`: only continue checks that have saved `MD_UUID_*` state.
- `--start`: continue saved checks and start arrays not marked as checked.
- `--restart`: remove `Checked_*` files and exit, allowing previously finished arrays to be checked again.
- No mode: start fresh from zero on all arrays, deleting old checked and checkpoint files.

## Options

- `--duration <time-offset>` computes an end time with `date --date` and stops checks after that budget.

## Main Flow

- Logs to journald stderr when run under systemd (`INVOCATION_ID` set), otherwise uses `logger`.
- Finds md devices through `/sys/block/*/md/sync_action`.
- Skips arrays whose `sync_action` is not `idle`.
- Resolves `/dev/...` names from sysfs `uevent`.
- Uses `BINDIR/mdadm --detail --export` to obtain `MD_UUID`.
- Stores checkpoints in `/var/lib/mdcheck/MD_UUID_$UUID`; finished markers use `/var/lib/mdcheck/Checked_$UUID`.
- Writes `sync_min` and then `check` to start or resume checks.
- While under a duration budget, polls `sync_action` and `sync_completed`, updating checkpoints until all finish or time expires.
- On exit cleanup, stops still-running checks by writing `idle`, stores current `sync_min`, removes temp file, and logs pause positions.

## Invariants and Risks

- State is keyed by md UUID, not device name, so renamed arrays can continue checks.
- The script assumes md sysfs paths and mdadm export output are trustworthy local interfaces.
- `BINDIR` is expected to be substituted by the build/install environment.
- Cleanup trap is central to time-budget behavior; premature termination records restart position.
