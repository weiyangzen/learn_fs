# File Research: sources/block-storage/vdo/utils/vdo/vdostats.c

## Purpose

`vdostats.c` implements `vdostats`, a command-line utility that queries running VDO device-mapper targets and displays configuration/statistics information.

It supports default `df`-style output and verbose aligned output through `vdo_write_stats()`.

## Command-Line Interface

Usage:

```text
vdostats [--help] [--version] [options...] [device [device ...]]
```

Options:

- `-h`, `--help`
- `-a`, `--all`: compatibility alias for verbose.
- `--human-readable`
- `--si`: SI units, implies human-readable.
- `-v`, `--verbose`
- `-V`, `--version`

If no devices are supplied, all running VDO devices are queried.

## Output Styles

`enum style`:

- `STYLE_DF`: default concise table.
- `STYLE_YAML`: verbose output.

Verbose is enabled by `-a` or `-v`, and causes each selected device to be printed as:

```text
<device> :
 <aligned verbose stats from vdo_write_stats()>
```

## Main Flow

`main()`:

1. Registers status codes.
2. Parses arguments.
3. Sets verbose style if requested.
4. Calls `enumerate_devices()` to list running VDO dm targets.
5. If no device arguments:
   - Calculates max display name length from all VDO target names.
   - Processes every VDO target.
6. If device arguments are present:
   - Calculates max display name length from argument basenames.
   - Resolves each argument through `transformDevice()`.
   - Processes matching devices.
7. Frees path array.

## Device Enumeration

`enumerate_devices()`:

1. Runs `dmsetup ls --target vdo` once to count lines.
2. Allocates `vdoPaths`.
3. Runs `dmsetup ls --target vdo` again.
4. Parses each line as:
   ```text
   name (major, minor)
   ```
5. Stores:
   - `name`
   - `resolvedName = dm-<minor>`
   - `resolvedPath = /dev/dm-<minor>`

## Device Resolution

`transformDevice()` matches user input against known VDO paths by:

- exact dmsetup target name
- resolved `dm-N` name
- `realpath()` result compared to `/dev/dm-N`

This allows callers to pass either target names or device paths.

## Stats Query

`process_device(original, name)`:

1. Builds command:
   ```c
   dmsetup message <name> 0 stats
   ```
2. Runs it with `popen()`.
3. Reads one stats line into `statsBuf[8192]`.
4. Calls `read_vdo_stats(statsBuf, &stats)`.
5. Displays according to current style:
   - `displayDFStyle()`
   - `vdo_write_stats()`
6. Checks `pclose()` status and fails if dmsetup returned nonzero.

## DF-Style Calculations

`getDFStats()` computes:

- `size = physical_blocks`
- `used = data_blocks_used + overhead_blocks_used`
- `available = size - used`
- `usedPercent = rounded used / size`
- `savingPercent = (logicalUsed - dataUsed) / logicalUsed`, or zero if no logical usage.

`displayDFStyle()` prints a header once, then rows with:

- Device
- Size or 1K-blocks
- Used
- Available
- Use%
- Space saving%

If `stats->in_recovery_mode`, used/available/percent/savings fields are printed as `N/A`.

Human-readable display uses `printSizeAsHumanReadable()`, with divisor `1024` by default or `1000` under `--si`.

## Dependencies

Includes:

- System: `linux/limits.h`, `err.h`, `errno.h`, `fcntl.h`, `getopt.h`, `libgen.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/stat.h`, `unistd.h`
- Utility/VDO: `errors.h`, `logger.h`, `memory-alloc.h`, `statistics.h`, `status-codes.h`, `vdoStats.h`

It depends on:

- `read_vdo_stats()` from the stats reader side.
- `vdo_write_stats()` from `vdoStatsWriter.c`.
- External `dmsetup`.

## Notable Behaviors and Risks

- `process_device()` builds a shell command with `sprintf(dmCommand, "dmsetup message %s 0 stats", name)`. Device names originate from `dmsetup` enumeration when valid, which mitigates but does not eliminate shell-command concerns.
- `statsBuf` is fixed at 8192 bytes; if the kernel stats message grows beyond one line or that size, parsing may truncate.
- `displayDFStyle()` uses `strdup(path)`, then `basename()`, and does not check `strdup()` failure.
- `enumerate_devices()` uses `getline()` but does not free `dmsetupLine`; process lifetime is short, but it is still a small leak.
- The output table width adapts to selected names through `maxDeviceNameLength`.
