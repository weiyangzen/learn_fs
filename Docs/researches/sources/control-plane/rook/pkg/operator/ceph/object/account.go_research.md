# sources/control-plane/rook/pkg/operator/ceph/object/account.go

## Purpose
`account.go` provides thin, validation-focused wrappers around the go-ceph RGW Admin Ops account and user APIs. It is the object package's backend layer for creating, reading, modifying, and deleting RGW accounts and their account-root users.

## Important APIs, Types, and Functions
The account functions all accept a `context.Context` and an `*AdminOpsContext` containing a configured `*admin.API`. `GetAccount`, `CreateAccount`, `ModifyAccount`, and `DeleteAccount` wrap `AdminOpsClient.GetAccount`, `CreateAccount`, `ModifyAccount`, and `DeleteAccount`. `CreateAccountRootUser`, `GetAccountRootUser`, `ModifyAccountRootUser`, and `DeleteAccountRootUser` wrap the corresponding `admin.User` APIs. Validation rejects empty account IDs, account names, user IDs, or user account IDs before contacting RGW.

## Control Flow, State, and Persistence
Each function performs local argument validation, delegates exactly one Admin Ops request, wraps any error with object identity context, and returns the RGW response. Persistent state is entirely in RGW: account records, account names, user records, generated credentials, and account-root flags. The wrappers do not write Kubernetes status or Secrets; the account controller uses them to do that.

## Dependencies and Integration Points
The file depends on `github.com/ceph/go-ceph/rgw/admin` and `github.com/pkg/errors`. Its primary consumers are the `object/account` controller methods `reconcileAccount`, `deleteAccount`, and `reconcileRootUser`. It also relies on error identity from go-ceph, such as `admin.ErrNoSuchKey`, `admin.ErrAccountAlreadyExists`, and `admin.ErrNoSuchUser`, being preserved through `errors.Wrapf()` for controller comparisons.

## Risks
The wrappers assume `adminOpsContext` and `AdminOpsClient` are non-nil; callers must initialize them before use. `CreateAccountRootUser` requires `user.AccountID`, but `ModifyAccountRootUser` only validates `user.ID`, so accidental account reassignment constraints are left to RGW. User functions assume the go-ceph API maps RGW error codes consistently enough for controller idempotency logic.

## Test Signals
This file has no dedicated direct unit test in the requested set, but it is exercised indirectly by `object/account/controller_test.go` using `object.MockClient` and go-ceph `admin.New()`. Those tests verify successful account creation/update/deletion, not-found idempotency, account-conflict errors, root-user creation/update/deletion, and Secret reconciliation.
