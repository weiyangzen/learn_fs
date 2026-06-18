# sources/distributed-fs/orangefs/src/client/webpack/d.s3/mod_orangefs_s3.c

## Purpose
This file implements an Apache httpd content/authentication module that exposes an Amazon S3-like REST surface over an OrangeFS/PVFS2 namespace. It maps buckets to directories under a configured `BucketRoot`, maps objects to PVFS files, stores S3 metadata in PVFS extended attributes, and authenticates requests using an Apache `AuthType AWS` hook with configured access keys.

## Important APIs, types, and functions
- Apache module entry points: `orangefs_s3_module`, `orangefs_s3_cmds`, `orangefs_s3_register_hooks`, `orangefs_s3_handler`, `orangefs_s3_authenticate_aws_user`, `orangefs_s3_post_config`.
- Server configuration: `orangefs_s3_config` holds `bucket_root`, `PVFSInit`, root owner/display values, resolved `pvfs_path`, `awsAccounts`, resolved `fsid`, and a `quit` flag used by recursive listing.
- Request context: `orangefs_s3_request` wraps the Apache `request_rec`, config, APR pool, parsed query params, user/root PVFS credentials, and authenticated name fields.
- S3 account config: `orangefs_s3_aws_account` stores access id, secret key, uid, and gid configured by `AWSAccount`.
- PVFS-backed object operations: `orangefs_s3_put_object`, `orangefs_s3_get_object`, `orangefs_s3_delete_object`, `orangefs_s3_copy_object` (stub).
- Bucket/service operations: `orangefs_s3_put_bucket`, `orangefs_s3_get_bucket`, `orangefs_s3_delete_bucket`, `orangefs_s3_get_service`, and placeholder subresource handlers for ACL/lifecycle/policy/location/logging/notification/versioning/website.
- Helpers: `orangefs_s3_load_post_data`, `parse_form_from_string`, `orangefs_s3_recurse`, `orangefs_s3_write_post_data_ref`, `orangefs_s3_authorized`, `orangefs_s3_mkdir_p`, `orangefs_s3_get_signature_data`, `orangefs_s3_get_aws_auth`.

## Control flow
Apache calls `orangefs_s3_authenticate_aws_user` during check-user-id. It accepts only `AuthType AWS`, parses `Authorization: AWS access_id:base64_signature`, looks up the configured account, builds a StringToSign, computes an HMAC-SHA1 with the configured secret key, and exports `AUTHENTICATE_CN`, `AUTHENTICATE_UIDNUMBER`, and `AUTHENTICATE_GIDNUMBER` into the request environment.

The content handler accepts only handler name `orangefs_s3`, reads those environment values, builds PVFS credentials plus a root credential, parses query parameters, and calls `orangefs_s3`. `orangefs_s3` resolves `BucketRoot` to an fs id and PVFS path for every request, then routes by host style and URI style: service request `/`, bucket request, or object request. Object `GET`, `PUT`, and `DELETE` call PVFS lookup/read/write/remove helpers. Bucket `GET`, `PUT`, and `DELETE` list, create, and remove PVFS directories.

Bucket listing uses `PVFS_sys_lookup` on the bucket directory, emits S3 XML, then recursively walks with `orangefs_s3_recurse`; `orangefs_s3_get_bucket_recurse` emits only non-directory entries as `<Contents>`. Service listing reads one batch of up to 60 entries under the bucket root and filters entries through `orangefs_s3_authorized`.

## State and persistence behavior
Persistent state lives in OrangeFS objects and extended attributes. Bucket and object owners are stored in `user.s3.owner.id` and `user.s3.owner.display-name`; object ETag and size are stored in `user.s3.entity-tag` and `user.s3.size`. PUT object writes request body bytes to the PVFS file, computes MD5, sets ETag/size/owner xattrs, and returns the ETag response header. GET object reads size and ETag xattrs if present, then streams PVFS file contents unless the HTTP method is `HEAD`.

Runtime state is per-request APR pool allocation plus server config. `awsAccounts` persists in the Apache server config pool. PVFS initialization is controlled by the `PVFSInit` directive so only one OrangeFS module initializes PVFS defaults when multiple modules are loaded.

## Dependencies and integration points
The file integrates Apache httpd/APR hooks and tables, PVFS2 sysint APIs, OpenSSL HMAC/EVP, libxml initialization, Unix passwd lookup, and S3-compatible HTTP clients. It expects upstream Apache authentication configuration to set `AuthType AWS` and the module handler to be bound to requests. `prepare.sh`/`pvfsinit.sh` in the same webpack area support module build and httpd `PVFSInit` coordination.

## Risks and edge cases
- AWS signature canonicalization is incomplete: `x-amz-*` headers are not lowercased, sorted, unfolded, or duplicate-collapsed, and canonical subresources are not appended. Interoperability with real S3 clients is fragile.
- `orangefs_s3_get_aws_auth` base64-decodes the signature and compares raw HMAC bytes, while classic S3 Authorization carries a base64 HMAC string after the colon. Any mismatch in expected encoding can reject valid clients.
- `apr_table_elts` is iterated as if header entries are triples (`headers->nelts*3` and `const char **`), but APR table entries are `apr_table_entry_t`; this can read invalid memory.
- `orangefs_s3_authorized` checks only owner id and has an empty ACL branch, so configured S3 ACL constants are not enforced.
- `parse_form_from_string` mutates `r->args` directly, which may surprise later Apache consumers.
- Request body loading/writing repeatedly reallocates APR buffers and lacks content-length limits. Large PUTs can consume memory or stream inefficiently.
- `orangefs_s3_mkdir_p` can recurse with `parent_path == NULL` for malformed relative paths and uses decimal literals for POSIX modes.
- XML responses interpolate unescaped bucket/object/metadata strings, so object names or display names containing XML-sensitive characters can produce invalid or unsafe XML.
- Object overwrite writes from offset 0 but does not visibly truncate existing larger files.
- Some PVFS request objects are freed only after loops; error paths may leak PVFS request handles or hints.
- Many S3 features are stubs returning `OK`, empty XML, or fixed errors; copy object is a no-op returning success.

## Test signals
Useful tests include Apache module load with multiple OrangeFS modules and `PVFSInit`, valid/invalid AWS signatures, path-style and virtual-host-style bucket routing, PUT/GET/HEAD/DELETE object round trips, overwrite with shorter object, bucket create/list/delete, non-owner service listing filtering, object names requiring XML escaping, large streaming PUT/GET, and real S3 client compatibility for canonicalized `x-amz-*` headers and subresources.
