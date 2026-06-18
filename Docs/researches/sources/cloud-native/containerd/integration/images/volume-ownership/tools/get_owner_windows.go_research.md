# sources/cloud-native/containerd/integration/images/volume-ownership/tools/get_owner_windows.go

## Purpose

This Windows helper prints the owner account and SID for a file or directory. It is built into Windows volume-ownership fixture images to support ownership validation.

## Important APIs, Types, And Functions

- `main` validates it received one path argument, checks the path exists, reads security information, resolves the owner SID to an account, and prints `account:sid`.
- `windows.GetNamedSecurityInfo` retrieves owner and DACL information.
- `sid.LookupAccount(".")` resolves the SID locally.

## Control Flow

The program exits with usage text if the argument count is wrong. It `Stat`s the target, fetches Windows file security info, obtains the owner SID, resolves it, and prints a compact result. Errors are fatal through `log.Fatal`.

## State And Persistence Behavior

The helper is read-only. It inspects filesystem ACL/owner metadata and writes only stdout/stderr.

## Dependencies And Integration Points

It depends on `golang.org/x/sys/windows` and is compiled by the volume-ownership Makefile for Windows fixture images.

## Risks And Edge Cases

It is Windows-only by API usage even though there is no build tag. Building it for non-Windows would fail; the Makefile explicitly sets `GOOS=windows`. Account lookup can fail for unresolvable SIDs.

## Test Signals

Windows volume ownership tests can execute this helper and compare the printed owner information.
