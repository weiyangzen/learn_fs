# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_acl.go

## Purpose
Implements S3 object ACL retrieval and update handlers. It resolves regular or versioned object entries, formats ACL responses from entry metadata, enforces owner/admin/WRITE_ACP permissions, parses canned/XML ACL requests, and persists ACL metadata back to the filer entry.

## Important APIs, Types, And Functions
`GetObjectAclHandler` handles `GET Object acl`; `PutObjectAclHandler` handles `PUT Object acl`. They use `s3_constants.GetBucketAndObject`, `validateTableBucketObjectPath`, `checkBucket`, `isVersioningConfigured`, `getSpecificObjectVersion`, `getLatestObjectVersion`, `fetchObjectEntryRequired`, `GetAcpGrants`, `buildAccessControlList`, `ExtractAcl`, `AssembleEntryWithAcp`, `getBucketConfig`, `isUserAdmin`, `iam.authRequest`, `Identity.CanDo`, and filer `UpdateEntry`.

## Control Flow
Both handlers validate path and bucket existence, read optional `versionId`, check bucket versioning, then resolve either the specific version, latest version, or non-versioned entry. Delete markers are treated as missing keys. `GetObjectAclHandler` extracts owner id from `ExtAmzOwnerKey`, falls back to the request account id, resolves display name through IAM, builds `AccessControlPolicy`, and writes XML.

`PutObjectAclHandler` resolves the same target entry, determines the current object owner, and if the caller is not admin requires both ownership and a specific `WriteAcp:<bucket>/<object>` authorization. It reads bucket ownership config, extracts and validates ACL grants, assembles ACL metadata into the entry, calculates the correct update directory for versioned, null, or non-versioned entries, and calls `UpdateEntry`.

## State And Persistence
GET is read-only. PUT mutates the target entry's extended ACL metadata and owner metadata via `AssembleEntryWithAcp`, then persists the whole entry to either the bucket directory or the object's `.versions` directory. It relies on existing `Entry.Name` remaining valid for the target directory.

## Dependencies And Integration Points
The file integrates ACL XML models, IAM account display lookup and auth, bucket ownership controls, versioning layout, delete-marker metadata, S3 account headers, and filer metadata updates.

## Risks And Test Signals
Risks include incorrect update directory selection for latest version versus null version, insufficient WRITE_ACP authorization modeling, stale entry overwrites through whole-entry `UpdateEntry`, delete marker handling differences from AWS, and fallback owner behavior when metadata is missing. Tests should cover ACL GET/PUT for non-versioned objects, versioned specific versions, latest null versions, delete markers, admin override, non-owner denial, bucket-owner-enforced modes, and XML/canned ACL parsing.
