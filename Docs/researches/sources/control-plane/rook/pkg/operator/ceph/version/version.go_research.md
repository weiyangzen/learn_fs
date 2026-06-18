# sources/control-plane/rook/pkg/operator/ceph/version/version.go

Purpose: defines Ceph version representation, supported-release constants, parsing from `ceph --version`, comparisons, and external-cluster compatibility validation.

Important APIs/types/functions: `CephVersion`, `Minimum`, `Squid`, `Tentacle`, `Umbrella`, `supportedVersions`, regex patterns, `String`, `CephVersionFormatted`, `ReleaseName`, `ExtractCephVersion`, `Supported`, `Unsupported`, `isRelease`, `isExactly`, `IsAtLeast`, release-specific helpers, `IsIdentical`, `IsSuperior`, `IsInferior`, and `ValidateCephVersionsBetweenLocalAndExternalClusters`.

Control flow: parsing uses regexes to extract major/minor/extra, optional numeric build suffix, and optional commit ID. Support checks match by major release, while unsupported checks match exact versions from a currently empty list. Comparison helpers manually compare major, minor, extra, build, and in `IsSuperior`, any commit ID difference at otherwise equal version counts as superior. External validation rejects external versions before Ceph 15, rejects local versions higher than external, warns but allows external minor/major versions higher than local, and allows identical versions.

State and persistence behavior: no persistence. Package globals define current supported release policy.

Dependencies/integration: used by operator controllers and Ceph client code to gate features and validate cluster compatibility. Depends only on regexp/strconv/fmt, capnslog, and pkg/errors.

Risks: supported versions must be maintained with Ceph release lifecycle. `IsSuperior` treating different commit IDs as superior is asymmetric and may surprise callers. `Unsupported` comment says "supported" but checks unsupported list. Build regex only captures numeric build after a hyphen; other version forms intentionally fail.

Test signals: `version_test.go` covers formatting, release names, parsing release/development builds, failed no-version parsing, support checks, comparisons, external-version validation, and empty unsupported list behavior.
