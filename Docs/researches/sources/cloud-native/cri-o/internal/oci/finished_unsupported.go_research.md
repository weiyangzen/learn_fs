# sources/cloud-native/cri-o/internal/oci/finished_unsupported.go

## Purpose
Non-Linux fallback for container finish time extraction.

## Behavior, Integration, and Risks
`getFinishedTime` returns `fi.ModTime()` instead of platform-specific creation/change time. It keeps exit-file status code portable but may be less semantically accurate than Linux ctime. It is used by `runtime_oci.go` when reading `dir/exit`.
