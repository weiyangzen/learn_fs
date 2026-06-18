# sources/cloud-native/moby/daemon/volume/mounts/windows_parser.go

## Purpose
Windows mount parser and validator for raw and structured mount specs, including bind mounts, named volumes, and named pipes.

## Important APIs, Types, And Functions
Defines regex fragments for host dirs, names, reserved names, named pipes, sources, destinations, and modes. `windowsParser` implements `Parser` methods: `ParseMountRaw`, `ParseMountSpec`, `ValidateMountConfig`, `ParseVolumesFrom`, `ReadWrite`, `ValidateVolumeName`, tmpfs/default methods, and `HasResource`.

## Control Flow
Raw parsing lowercases and splits via named regex groups, rejects malformed specs, detects attempts to map files as anonymous local volumes, and validates reserved names. Structured validation enforces exclusive options, non-root/non-empty targets, destination regex, bind source absolute/existing/directory rules, volume subpath locality and name validation, and named pipe source/target rules. Parsed mountpoints normalize slashes to backslashes, trim trailing backslashes except drive roots, set drivers/copy data for volumes, and mark read-only based on mode.

## State And Persistence
Parser state is limited to `fileInfoProvider`; no persistence.

## Dependencies And Integration Points
Used by Windows daemon mount validation and by LCOW through embedding. Depends on lazy regexes, API mount types, shared validation/copy helpers, and filesystem stat provider.

## Risks
Regex grammar is dense and highly compatibility-sensitive. Lowercasing raw specs may affect case-preserving expectations. Reserved device names and named pipe handling are security-sensitive. Windows tmpfs/image/resource methods intentionally return unsupported defaults.

## Test Signals
Windows parser tests cover many raw forms, reserved names, file-vs-directory checks, named pipes, mode parsing, structured validation, and file-info error propagation.
