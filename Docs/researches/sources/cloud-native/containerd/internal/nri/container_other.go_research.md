# sources/cloud-native/containerd/internal/nri/container_other.go

## Purpose
Provides non-Linux container-to-NRI conversion without Linux-specific fields.

## Important APIs, Types, And Functions
`containerToNRI` simply returns `commonContainerToNRI(ctr)`.

## Control Flow
Selected for `!linux` builds to keep the API portable.

## State And Persistence
No state.

## Dependencies And Integration Points
Depends on NRI adaptation types through the common conversion.

## Risks
NRI plugins on non-Linux receive no Linux payload. Callers must not expect Linux-specific adjustments to apply.

## Test Signals
No direct tests; compile coverage on non-Linux is the main signal.
