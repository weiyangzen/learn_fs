# sources/distributed-fs/juicefs/pkg/object/ufile.go

Purpose: implements UCloud UFile storage by extending `RestfulStorage` with UFile signing, bucket creation, copy acceleration, listing, and multipart support.

Important APIs and types: `ufile` embeds `RestfulStorage`. `ufileSigner` builds the UCloud authorization header. Additional types model list and multipart JSON responses. Methods include `Create`, `parseResp`, `Copy`, `List`, multipart create/upload/abort/complete/list, `Limits`, and `newUFile`.

Control flow and state: `Create` calls UCloud's API service with query-string signature and treats duplicate bucket/create success responses as nil. `Copy` tries UFile `uploadhit` using source ETag and content length, falling back to read-and-write copy. `List` rejects delimiters despite having dead common-prefix handling, caps max keys, parses JSON, and uses the last returned key as marker because UFile's `NextMarker` is unreliable. Multipart upload adjusts part numbers to UFile's zero-based convention.

Persistence and integration: data persists in UFile and generic CRUD comes from signed REST calls. Registered as `ufile`.

Risks and test signals: copy/list/multipart rely on provider quirks and fallback behavior. `AbortUpload` ignores response cleanup. Delimiter listing is unsupported. No UFile-specific tests are included.
