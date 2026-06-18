# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Info.plist.in

Purpose: PackageMaker info plist template for the main OpenAFS package.

Important APIs/types/functions: sets bundle identifier `org.openafs.OpenAFS.pkg`, bundle name/version placeholders, root authorization, install location `/`, root-volume-only, no restart, non-relocatable flags, and format version.

Control flow: metadata only.

State and persistence: becomes package metadata/receipt after build and install.

Dependencies/integration: consumed by `buildpkg.sh.in`; paired with resource scripts such as postinstall and preupgrade.

Risks and test signals: duplicate `IFPkgFlagAllowBackRev` keys appear, although both are true here. PackageMaker compatibility on newer macOS is a broader risk. Validate with package build and installer metadata inspection.
