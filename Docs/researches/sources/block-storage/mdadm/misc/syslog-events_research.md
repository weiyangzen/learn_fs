# File Research: sources/block-storage/mdadm/misc/syslog-events

## Role

`misc/syslog-events` is a sample shell event handler for `mdadm --follow --program=...`.

## Behavior

- Receives event, md device, and optional component disk as `$1`, `$2`, and `$3`.
- Uses syslog facility `kern` and tag `mdmonitor`.
- Maps `Fail*` events to `error`, `Test*` events to `debug`, and all others to `info`.
- Builds a short message including related disk when present.
- Executes `logger` with the selected facility/priority.

## Invariants

The script is intentionally minimal and stateless. It demonstrates the argument contract expected by mdadm monitor alert programs.
