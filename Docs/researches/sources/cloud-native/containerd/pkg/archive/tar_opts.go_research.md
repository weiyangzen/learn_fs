<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts.go -->
# sources/cloud-native/containerd/pkg/archive/tar_opts.go

Purpose: option and callback definitions for archive apply and diff operations.

Important APIs and types: `ApplyOptions`, `ApplyOpt`, `Filter`, `ConvertWhiteout`, `WithFilter`, `WithConvertWhiteout`, `WithNoSameOwner`, `WithParents`, `WriteDiffOptions`, `WriteDiffOpt`, and `WithSourceDateEpoch`.

Control flow and state: option functions mutate option structs before `Apply` or `WriteDiff` run. `ApplyOptions` can override filtering, whiteout conversion, parent metadata lookup, ownership preservation, and the apply implementation. `WriteDiffOptions` can set parent layers, implementation override, and source date epoch.

Dependencies and integration: the option structs are consumed by `tar.go`; platform-specific option files add Linux overlay and Windows layer variants.

Risks and test signals: options can significantly change destructive behavior, particularly custom whiteout conversion and custom apply/diff functions. Tests cover filters implicitly through apply paths and source-date behavior through `TestSourceDateEpoch`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts.go -->
