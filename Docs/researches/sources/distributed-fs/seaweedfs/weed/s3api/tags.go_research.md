## sources/distributed-fs/seaweedfs/weed/s3api/tags.go

Purpose: represents S3 object tagging XML, converts between XML tag sets and maps, parses `x-amz-tagging` style query strings, and delegates validation.

Important APIs/types: `Tag`, `TagSet`, `Tagging`, `ToTags`, `FromTags`, `parseTagsHeader`, and `ValidateTags`.

Control flow: `ToTags` folds XML tags into a map where duplicate keys overwrite. `FromTags` creates XML with the S3 namespace and stable key ordering. `parseTagsHeader` splits on `&`, then `=`, URL-decodes keys and values, allows empty values, and returns decoding errors for malformed percent escapes. `ValidateTags` delegates to `s3tables.ValidateTags`, sharing key/value limits and character rules.

State and dependencies: stateless conversions. Depends on XML, URL decoding, sorting, SeaweedFS string splitting, and S3 Tables tag validation.

Risks: `strings.Split` rather than `SplitN` ignores unencoded `=` inside values, so callers must URL-encode special characters. Tests cover encoded timestamps, keys, values, empty values, invalid encoding, plus signs, and encoded equals.
