# sources/distributed-fs/openafs/src/packaging/MacOS/buildpkg.sh.in

Purpose: Mac packaging script template that stages OpenAFS files, builds PackageMaker packages, and wraps them into a DMG.

Important APIs/types/functions: command modes are default, `-firstpass`, and `-secondpass`. Key variables include `BINDEST`, `RESSRC`, `majorvers`, `RELNAME`, `PKGROOT`, `PKGRES`, `DPKGROOT`, `DPKGRES`, and `PACKAGEMAKER`. It builds main and debug packages, resource directories, symlinks into `/usr`, package plugins, and final hybrid/compressed DMG.

Control flow: first pass validates `CellServDB`, required resources, and binary destination, then creates package roots with preference panes, SecurityAgent plugin, tools, launchd plist, OpenAFS config, kernel extension, cache directories, symlinks, man pages, and ownership/mode settings. For newer systems it separates debug symbols. Second pass creates resource trees, runs PackageMaker, optionally embeds installer plugins, assembles a `dmg` directory, copies uninstall/background assets, and uses `hdiutil` to create the final DMG.

State and persistence: creates and deletes staging directories and package/DMG artifacts in the current directory; downloads `CellServDB` when curl is present.

Dependencies/integration: depends on macOS tools: PackageMaker, mdfind, pax, curl, hdiutil, strip, gzip, chown/chmod. It consumes many MacOS packaging resource files and a `make dest` output tree.

Risks and test signals: PackageMaker is obsolete on modern macOS. Numerous unquoted paths risk breakage with spaces. Network download uses plain HTTP. Version mapping stops at Darwin major 15. Test by running both passes on a known-supported macOS build host and installing the resulting DMG.
