# sources/cloud-native/containerd/core/images/archive/reference.go

Purpose: reference translation helpers for image archive import/export.

Important APIs/functions: `FilterRefPrefix`, `AddRefPrefix`, `refTranslator`, `isImagePrefix`, `normalizeReference`, `familiarizeReference`, `ociReferenceName`, and `DigestTranslator`.

Control flow and state: translators return closures. Tag-only references are converted to `image:tag`; full references containing `/`, `:`, or `@` are either returned or filtered based on prefix. Normalize/familiarize delegate to Docker distribution reference parsing. `ociReferenceName` prefers the parsed object component when it is not a digest object, otherwise uses the full name. `DigestTranslator` creates `prefix@digest` strings.

Dependencies and integration: containerd reference parser, Docker distribution reference parser, go-digest. Used by archive importer/exporter to set `io.containerd.image.name`, OCI ref names, and Docker `RepoTags`.

Risks: the heuristic for full references is simple and may classify unusual names based on punctuation. Prefix checking avoids partial namespace matches by requiring delimiter after prefix. OCI ref names are constrained by OCI grammar, so digest references use the full name.

Test signals: no direct tests here. Archive reference tests should cover tag-only translation, prefix filtering, partial prefix rejection, normalized Docker names, familiar tags, and digest references.
