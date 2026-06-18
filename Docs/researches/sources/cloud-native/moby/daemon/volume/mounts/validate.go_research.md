# sources/cloud-native/moby/daemon/volume/mounts/validate.go

## Purpose
Shared mount validation error helpers and option exclusivity checks.

## Important APIs, Types, And Functions
`errMountConfig` wraps a `mount.Mount` and underlying validation error. Helpers include `errBindSourceDoesNotExist`, `errExtraField`, `errMissingField`, and `validateExclusiveOptions`.

## Control Flow
Platform parsers call `validateExclusiveOptions` before type-specific checks. It rejects bind, volume, image, tmpfs, and cluster option structs when the mount type does not match.

## State And Persistence
No state is mutated.

## Dependencies And Integration Points
Used by Linux, Windows, and LCOW validators to produce consistent API error messages for invalid mount configs.

## Risks
Error text is user-facing and tested. New mount types/options must update exclusivity checks or invalid cross-type fields may pass silently.

## Test Signals
`validate_test.go` exercises missing fields, extra option structs, unknown type, missing bind source, and image-specific option exclusivity.
