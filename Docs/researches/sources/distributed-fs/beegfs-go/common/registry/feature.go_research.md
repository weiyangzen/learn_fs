# sources/distributed-fs/beegfs-go/common/registry/feature.go

Purpose: centralizes string constants for known registry capability feature names.

Important API is `FeatureFilterFiles = "filter-files"`. This is used by RST job request preparation when filter expressions are supplied, requiring the remote BeeRemote registry to advertise filter support before compiling and applying file filters.

Control flow and state are absent; this file is a compile-time constants holder.

Dependencies: none beyond the package itself. Integration points are feature-gated callers and `ComponentRegistry.RequireFeature`.

Risks: feature names are wire/API contracts; renaming breaks compatibility with services that publish the old capability name. New features should be added here to avoid ad hoc strings.

Test signals: no direct tests for the constant. Its behavior is indirectly covered when callers require feature strings against registry responses.
