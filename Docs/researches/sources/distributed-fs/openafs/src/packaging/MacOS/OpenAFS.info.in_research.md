# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.info.in

Purpose: legacy PackageMaker plain-text package info template for older macOS packaging paths.

Important APIs/types/functions: key/value metadata for title, version, description, default location, authorization, masks, relocatability, reboot, fat install, root volume restriction, and back-rev behavior.

Control flow: metadata only; used by older packaging mode in `buildpkg.sh.in` for major versions below 7.

State and persistence: substituted into package metadata during build.

Dependencies/integration: relies on `@PACKAGE_VERSION@` substitution and old PackageMaker command syntax.

Risks and test signals: legacy format is likely unsupported on modern build hosts. Only old macOS package builds validate it.
