# sources/cloud-native/moby/daemon/internal/usergroup/parser.go

## Purpose
Provides small helpers to parse subordinate UID and GID ranges for a specific username from standard Linux files.

## Important APIs, Types, And Functions
Constants `subuidFileName` and `subgidFileName` point to `/etc/subuid` and `/etc/subgid`. `parseSubuid` and `parseSubgid` call `user.ParseSubIDFileFilter` and retain entries whose `sid.Name` equals the requested username.

## Control Flow
Each helper delegates parsing and filtering to `github.com/moby/sys/user`; no additional validation or sorting is done here.

## State And Persistence
Read-only access to subordinate ID files.

## Dependencies And Integration Points
Used by `createSubordinateRanges` to decide whether distro user creation already created ranges.

## Risks And Test Signals
Numeric uid aliases are not matched here, only names; `LoadIdentityMapping` has broader matching. Tests in `parser_test.go` exercise underlying parser behavior with comments and blank lines rather than these exact constants.
