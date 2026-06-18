# sources/distributed-fs/ceph/src/rgw/rgw_polparser.cc

## Purpose
`rgw_polparser.cc` is a small command-line utility that validates RGW IAM policy JSON files, optionally under a tenant context.

## Important APIs, Types, And Functions
`parse()` reads an input stream into a bufferlist and constructs `rgw::IAM::Policy`, reporting parse exceptions. `usage()` and `helpful_exit()` handle CLI messaging. `main()` initializes a Ceph context without daemon actions or monitor config, parses `--tenant/-t`, then parses stdin or listed files.

## Control Flow
The utility starts Ceph global initialization, processes help and tenant args, then iterates remaining file args. Missing files and parse failures set `success=false`; exit status is `0` only when all inputs parse.

## State And Persistence
It reads policy files/stdin only. No cluster metadata is written. Runtime state is limited to the Ceph context and optional tenant string.

## Dependencies And Integration Points
It depends on Ceph argument parsing, common/global init, bufferlist, and `rgw_iam_policy.h`. It is useful for developer/admin validation of IAM policy syntax and principal checks using `rgw_policy_reject_invalid_principals`.

## Risks And Test Signals
Risks include incomplete CLI validation, opening a missing file then still invoking parse on an unopened stream, and config-dependent principal validation. Tests should cover stdin, multiple files, unreadable files, tenant option, `-h`, invalid JSON, invalid principals, and exception reporting.
