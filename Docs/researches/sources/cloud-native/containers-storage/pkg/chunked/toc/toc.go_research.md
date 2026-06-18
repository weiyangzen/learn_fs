## sources/cloud-native/containers-storage/pkg/chunked/toc/toc.go

Purpose: extracts a TOC digest from image annotations for either eStargz or zstd:chunked layers without importing eStargz package code.

Important APIs/types/functions: `tocJSONDigestAnnotation` and `GetTOCDigest`.

Control flow: checks for both eStargz and zstd:chunked annotation keys, rejects ambiguous dual presence, parses whichever digest is present, or returns nil when neither exists.

State and persistence: stateless annotation-map inspection.

Dependencies and integration points: used by `storage_linux.go` after conversion and by callers wanting a format-neutral TOC digest. Depends on `minimal.ManifestChecksumKey` and OCI digest parsing.

Risks: nil digest is a valid "not present" result and must not be confused with parse success. Duplicate annotations are treated as hard error to avoid ambiguity.

Test signals: `toc_test.go` covers valid eStargz annotation, invalid digest, and no annotation. It does not cover the dual-annotation error or zstd key explicitly.
