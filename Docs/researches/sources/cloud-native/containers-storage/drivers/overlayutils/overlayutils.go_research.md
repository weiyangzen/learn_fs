<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlayutils/overlayutils.go -->
# sources/cloud-native/containers-storage/drivers/overlayutils/overlayutils.go

## Purpose
This utility file centralizes the error message for backing filesystems without d_type support.

## Important APIs, Types, And Functions
`ErrDTypeNotSupported(driver, backingFs string) error` builds a detailed message, adds XFS `ftype=1` guidance when relevant, and wraps `graphdriver.ErrNotSupported`.

## Control Flow
The function formats the message and returns a wrapped error in one path.

## State And Persistence
No state is read or written.

## Dependencies And Integration Points
`overlay.go` calls this from `supportsOverlay` after `fsutils.SupportsDType` fails. Wrapping `graphdriver.ErrNotSupported` lets higher layers classify the failure.

## Risks And Test Signals
The function is simple but user-facing; message changes can affect tests or documentation that match errors. No direct tests are present here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlayutils/overlayutils.go -->
