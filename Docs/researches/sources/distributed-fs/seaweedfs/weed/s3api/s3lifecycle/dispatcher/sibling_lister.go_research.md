# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dispatcher/sibling_lister.go

Purpose: implements `filerSiblingLister`, the `router.SiblingLister` adapter backed by a Seaweed filer client. It centralizes lifecycle queries over `.versions/<key>/` and bare-key null versions so dispatcher/router code does not reimplement version-layout knowledge.

Important APIs: `NewFilerSiblingLister`, `Survivors`, `ListVersions`, `LookupNullVersion`, and `LookupVersion`. `Survivors` counts version siblings with a limit of two, tracks a lone entry only when exactly one version exists, and checks the bare key as a null version. `ListVersions` pages with size 1024 and filters out directories, nil attributes, and entries without `ExtVersionIdKey`. `LookupNullVersion` returns the bare regular file or explicit directory-key marker plus an `explicit` null-version flag. `LookupVersion` maps version id to `v_<id>`.

Control flow and state: stateless except for `client` and `bucketsPath`. It normalizes bucket paths with `strings.TrimSuffix` and uses `util.NewFullPath` for trailing-slash object keys. Not-found is collapsed to nil/zero results for expected races; other filer errors propagate.

Dependencies/integration: depends on `filer_pb.SeaweedList`, `filer_pb.LookupEntry`, `s3_constants` version metadata keys, and router survivor interfaces. It feeds expired delete-marker and noncurrent-version routing decisions.

Risks: pagination relies on `lastName` progressing; version entries with absent/empty version ids are intentionally ignored. Directory-key markers must be distinguished from plain directories to avoid treating prefixes as null versions. NotFound behavior depends on `LookupEntry` normalization.

Test signals: `sibling_lister_test.go` covers not-found collapse, lone-entry clearing after count > 1, directory-key null markers, list filtering, 1024+ pagination, explicit null detection, `v_` lookup prefixing, and error propagation.
