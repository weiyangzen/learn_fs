# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Description.plist.in

Purpose: PackageMaker description plist template for the OpenAFS debug-symbol extension.

Important APIs/types/functions: defines package title, description, version placeholder, and delete warning field.

Control flow: metadata only; consumed by packaging tools.

State and persistence: substituted into package resources during build.

Dependencies/integration: paired with `OpenAFS-debug.Info.plist.in` and `buildpkg.sh.in` debug package construction.

Risks and test signals: stale or mismatched `@PACKAGE_VERSION@` substitution affects installer metadata. Package build output and installer UI verify it.
