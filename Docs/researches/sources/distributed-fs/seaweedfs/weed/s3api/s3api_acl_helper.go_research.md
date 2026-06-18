# sources/distributed-fs/seaweedfs/weed/s3api/s3api_acl_helper.go

## Purpose
`s3api_acl_helper.go` parses, validates, transforms, serializes, and renders S3 ACL grants. It supports ACL XML bodies, canned ACL headers, custom grant headers, account/email resolution, default private ACLs, and storing ACP data in filer entry metadata.

## Important APIs, Types, and Functions
Key types/functions are `AccountManager`, `ExtractAcl`, `ParseAndValidateAclHeadersOrElseDefault`, `ParseAndValidateAclHeaders`, `ParseAclHeaders`, `ParseCustomAclHeaders`, `ParseCustomAclHeader`, `ParseCannedAclHeader`, `ValidateAndTransferGrants`, `buildAccessControlList`, `GetAcpGrants`, and `AssembleEntryWithAcp`.

## Control Flow
`ExtractAcl` prefers an XML request body when present, verifies the ACP owner matches the immutable owner ID, and validates/transfers grants. If the body is empty, it parses headers. Header parsing gives custom grant headers priority for non-PutAcl operations, otherwise parses canned ACLs. Canned ACL handling creates grants for object writer, public/authenticated groups, log delivery, and bucket-owner read/full-control cases, with bucket-owner-preferred ownership able to switch owner ID during object upload. Validation resolves canonical IDs and email grantees through `AccountManager` and validates group URIs.

## State and Persistence Behavior
ACL owner and grants are stored in `filer_pb.Entry.Extended` under SeaweedFS extension keys. Grants are JSON-marshaled AWS SDK `s3.Grant` values. Missing grants render as a default owner full-control ACL for responses.

## Dependencies and Integration Points
The file depends on AWS SDK S3 ACL structs/XML utilities, SeaweedFS S3 constants/errors, filer protobuf entries, and request close utilities. It integrates with bucket/object ACL APIs and object metadata assembly.

## Risks and Edge Cases
`ParseCustomAclHeader` splits on `", "` and `"="`, so unusual spacing or quoted values containing `=` may fail or parse incorrectly. JSON unmarshal errors for quoted grant values are ignored, potentially producing empty IDs/emails that validation later catches if account lookup fails. `CannedAclAwsExecRead` is not implemented. Account manager correctness is security-critical for email-to-ID transfer.

## Test Signals
Tests should cover XML owner mismatch, body/header precedence, canned ACL variants, bucket-owner-preferred ownership, invalid group URIs, nonexistent canonical IDs/emails, default private ACL fallback, JSON persistence round trips, and malformed custom grant headers.
