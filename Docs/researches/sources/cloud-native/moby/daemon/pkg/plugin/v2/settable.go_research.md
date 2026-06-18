<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/settable.go

## Purpose
Parses and validates plugin setting assignment syntax used by `Plugin.Set`.

## Important APIs, Types, And Functions
`settable` holds `name`, `field`, and `value`. Helpers include `newSettables`, `newSettable`, `prettyName`, `isSettable`, and `updateSettingsEnv`. Allowed fields are defined for env, args, devices, and mounts.

## Control Flow
Assignments must be `<name>[.<field>][=<value>]`; leading `=` is invalid. Field is parsed from the last dot before `=`, with defaulting only when exactly one field is declared settable. `updateSettingsEnv` replaces an existing `NAME=` entry or appends a new one.

## State, Dependencies, And Integration Points
State changes are limited to env slices passed by pointer. It integrates with v2 plugin configuration mutation before save.

## Risks And Test Signals
Names containing dots may be interpreted as field syntax. Multiple settable fields require explicit field selection. Tests cover parsing, allowed-field checks, and env update ordering.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/settable.go -->
