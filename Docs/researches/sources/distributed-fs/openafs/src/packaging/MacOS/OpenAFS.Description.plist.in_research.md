# sources/distributed-fs/openafs/src/packaging/MacOS/OpenAFS.Description.plist.in

Purpose: PackageMaker description plist template for the main OpenAFS package.

Important APIs/types/functions: provides delete warning, description text, title `OpenAFS`, and `@PACKAGE_VERSION@`.

Control flow: metadata only.

State and persistence: substituted into installer package resources.

Dependencies/integration: used with `OpenAFS.Info.plist.in` by `buildpkg.sh.in`.

Risks and test signals: description says "client and server" while package contents/scripts focus heavily on client install; metadata should match actual packaging intent. Installer UI and package inspection validate substitution.
