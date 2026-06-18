# sources/distributed-fs/coda/coda-src/smon2/volusage.py

Purpose: Python utility that lists per-volume usage and activity from a server's `volutil getvolumelist` output.

Control flow: parses positional `host` and optional `--volutil`, runs `volutil -h <host> getvolumelist`, splits output lines, ignores short lines, extracts volume name, usage from hex field 6, partition from field 3, and activity from hex field 11, sorts by tuple `(partition, usage, volume, activity)`, and prints tabular lines.

State/persistence: read-only subprocess query; no local writes.

Dependencies, risks, tests: depends on Python 3, `volutil`, exact volume-list field layout, and successful command exit. Risks include uncaught `CalledProcessError`, uncaught `ValueError` on malformed hex fields, and no filtering by volume type. Test with fixture output containing partitions, short/malformed lines, high usage sorting, alternate volutil path, and server command failure.
