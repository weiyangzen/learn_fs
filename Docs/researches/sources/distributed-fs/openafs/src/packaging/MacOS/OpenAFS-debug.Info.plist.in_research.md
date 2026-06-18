# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS-debug.Info.plist.in

Purpose: PackageMaker info plist template for the optional OpenAFS debug package.

Important APIs/types/functions: sets bundle identifier `org.openafs.OpenAFS-debug.pkg`, bundle name, version placeholders, authorization action, install location `/`, root-volume-only, relocatability, restart behavior, and package format version.

Control flow: metadata only.

State and persistence: becomes package receipt/install metadata after substitution.

Dependencies/integration: used by `buildpkg.sh.in` when major macOS version is 9 or newer.

Risks and test signals: contains duplicate `IFPkgFlagAllowBackRev` keys with conflicting false/true values; plist consumers may choose the later value but ambiguity is risky. Test by building and inspecting the generated pkg metadata.
