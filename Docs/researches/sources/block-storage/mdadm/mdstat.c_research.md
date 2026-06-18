# File Research: sources/block-storage/mdadm/mdstat.c

## Role

`mdstat.c` parses `/proc/mdstat` into mdadm’s `struct mdstat_ent` linked list and provides wait/lookup helpers.

## Parser Behavior

`mdstat_read()`:

- Opens `/proc/mdstat`, or reuses a held fd when requested.
- Reads logical lines through `conf_line()` so continuation lines are folded.
- Skips `Personalities`, `read_ahead`, and `unused` lines.
- Accepts md lines whose devnm begins with `md` and is short enough for mdadm buffers.
- Extracts active/inactive state, RAID level, component member names, metadata version, raid disk count, `[UU_]` pattern, rebuild/resync/check/reshape progress, and delayed/pending/remote states.
- Reorders mdstat entries when md devices are components of other md devices, so components can appear before composites.
- Optionally reverses order for startup operations.

## Data Management

- `free_mdstat()` releases levels, patterns, metadata strings, member lists, and entries.
- `mdstat_close()` closes the held mdstat fd.
- `free_member_devnames()` and `add_member_devname()` manage component name lists.

## Lookups and Predicates

- `is_mdstat_ent_external()` detects `external:` metadata.
- `is_mdstat_ent_subarray()` detects external subarrays by checking the metadata suffix with `is_subarray()`.
- `is_container_member()` tests whether an mdstat entry belongs to a given external container.
- `mddev_busy()` checks whether a devnm appears in mdstat.
- `mdstat_find_by_member_name()`, `mdstat_by_component()`, and `mdstat_by_subdev()` find arrays by component or external subarray metadata and detach the returned entry from the temporary list.

## Waiting

- `mdstat_wait()` uses `select()` exceptional conditions on the held `/proc/mdstat` fd.
- `mdstat_wait_fd()` waits on mdstat plus another fd, using exceptional events for regular proc/sysfs-style fds and read events for non-regular fds.

## Invariants

- Returned detached entries from `mdstat_by_component()` and `mdstat_by_subdev()` must be freed by the caller with `free_mdstat()`.
- The parser is intentionally tolerant of historical mdstat formats and token order.
- `metadata_version` and member parsing are key dependencies for mdmon and mdmonitor external-array behavior.
