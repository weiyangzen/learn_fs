# sources/cloud-native/moby/daemon/volume/mounts/linux_parser_test.go

## Purpose
Linux parser tests for raw mount specs, structured mount validation, file-info error propagation, and tmpfs option serialization.

## Important APIs, Types, And Functions
Tests include `TestLinuxParseMountRaw`, `TestLinuxParseMountRawSplit`, `TestLinuxValidateMounts`, `TestLinuxParseMountSpecBindWithFileinfoError`, and `TestConvertTmpfsOptions`.

## Control Flow
Raw tests run valid and invalid string tables across destinations, bind paths, named volumes, rw/ro, SELinux labels, propagation modes, duplicate mode rejection, and invalid colon forms. Split tests compare complete `MountPoint` values. Structured validation checks bind, volume, invalid source, invalid type, and image behavior outside Windows. File-info tests ensure provider errors are returned instead of collapsed to missing-source errors. Tmpfs tests assert mode, size suffix, read-only, allowed options, and invalid option errors.

## State And Persistence
Uses temp dirs and mock file providers; no persistent daemon state.

## Dependencies And Integration Points
Depends on Linux parser, shared mocks, Docker API mount types, and cmp helpers.

## Risks
The tests document compatibility quirks such as empty mode versus explicit `rw`. Host mount setup is not exercised.

## Test Signals
Strong semantic signal for Linux mount spec compatibility, especially propagation/copy mode validation and file-info error fidelity.
