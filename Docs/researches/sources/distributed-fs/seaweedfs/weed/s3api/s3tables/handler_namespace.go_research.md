# sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_namespace.go

## Purpose
This file implements namespace create/get/list/delete operations within S3 table buckets.

## Important APIs and functions
`handleCreateNamespace`, `handleGetNamespace`, `handleListNamespaces`, and `handleDeleteNamespace` parse requests, validate namespace arrays, use bucket and namespace paths, read/write metadata, consult bucket policies/tags, enforce permissions, and write AWS JSON responses. Namespace metadata is stored in `ExtendedKeyMetadata`.

## Control flow and state behavior
Create validates ARN and namespace, loads bucket metadata and policy/tags, and has a compatibility branch that reconstructs missing bucket metadata for existing table-bucket entries. It authorizes `CreateNamespace`, checks namespace absence by looking for metadata, creates the namespace directory, and writes metadata with bucket owner as owner. Get loads namespace metadata and bucket policy/tags, authorizes `GetNamespace`, and returns not found on access denial to hide resource existence. List validates bucket, loads bucket metadata/policy/tags, authorizes `ListNamespaces`, then paginates bucket children, skipping hidden/non-directory entries, applying prefix, requiring metadata, and matching owner. Delete loads namespace metadata plus bucket policy/tags, authorizes, checks emptiness by listing children and treating metadata-bearing directories or files as children, then recursively deletes the namespace directory.

## Dependencies and integration points
The file depends on path/validation helpers, filer list/extended-attribute methods, bucket policy checks via `CheckPermissionWithContext`, bucket tags via `readTags`, and metadata structs from `utils.go`.

## Risks and edge cases
There are verbose log calls at create time, including an error-level "called" log that may be noisy. Namespace existence checks conflate missing metadata with missing entries except for the create compatibility branch. Create is not atomic across directory creation and metadata write. List pagination uses `maxNamespaces*2` without an explicit cap like bucket listing. Delete emptiness intentionally ignores empty directories without metadata, which may surprise callers if stray directories contain hidden state.

## Test signals
No direct namespace tests are included in this subset. Coverage should come from broader S3 Tables operation tests; important missing areas are metadata reconstruction, permission-hiding behavior, and delete emptiness semantics.
