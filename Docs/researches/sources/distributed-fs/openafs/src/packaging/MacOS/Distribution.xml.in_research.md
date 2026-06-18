# sources/distributed-fs/openafs/src/packaging/MacOS/Distribution.xml.in

Purpose: Mac Installer distribution XML template for the OpenAFS product package set.

Important APIs/types/functions: declares root-volume-only install, OS version bounds through placeholders, RAM installation check, title/background/readme/license, optional presentation extra content, choices for normal client and debug symbols, package references, and product version placeholder.

Control flow: consumed by Apple installer tooling, not executable code. User-facing choices include required normal OpenAFS client and optional debug extension.

State and persistence: template values are substituted during packaging; installer state is external.

Dependencies/integration: depends on build scripts supplying `%%OSVER_CUR%%`, `%%OSX_MAJOR_CUR%%`, `%%OSVER_NEXT%%`, `%%OSX_MAJOR_NEXT%%`, `%%PRES_EXTRA%%`, and `%%OPENAFS_VERSION%%`, plus package files named in `pkg-ref`.

Risks and test signals: mismatched package IDs or version placeholders break installer assembly. OS version bounds must track supported macOS releases. Validation is `productbuild`/Installer acceptance and test installs.
