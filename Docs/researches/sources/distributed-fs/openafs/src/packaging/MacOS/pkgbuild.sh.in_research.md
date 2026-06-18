<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/pkgbuild.sh.in -->
# sources/distributed-fs/openafs/src/packaging/MacOS/pkgbuild.sh.in

## Purpose
Builds the macOS OpenAFS installer package and distribution DMG from a `make dest` binary tree. It prepares a package root, installs OpenAFS tools, kexts, launchd files, config samples, debug symbols, preference pane resources, signs binaries and bundles when configured, creates component and product packages, optionally notarizes the DMG, and writes checksums.

## Important APIs, Types, And Functions
The shell script accepts signing identities (`--app-key`, `--inst-key`), notarization profile, CellServDB path, pass selection, and tracing. It uses package tools (`pkgbuild`, `productbuild`, `productsign`, `hdiutil`), signing tools (`codesign`, `kextutil`), archive/copy tools (`pax`, `gzip`, `strip`), checksum tools (`md5`, `shasum`), and many packaging resources from the same directory. Autoconf substitutions provide `@PACKAGE_VERSION@`, `@MACOS_APP_KEY@`, `@MACOS_INST_KEY@`, and `@MACOS_KEYCHAIN_PROFILE@`.

## Control Flow
Argument parsing enables pass 1, pass 2, or both. The script maps Darwin major versions to macOS release names and package compatibility values from Snow Leopard through Tahoe. Pass 1 validates or downloads CellServDB, verifies required resources and binaries, constructs `pkgroot`, `dpkgroot`, and `plugins`, copies bundles/tools/configuration, moves debug kext artifacts, strips the installed kext, signs files and bundles, validates older kext signatures, chooses `/usr` or `/opt/openafs` symlink layouts by OS version, and gzips/symlinks manpages. Pass 2 builds debug and distribution component packages, generates `Distribution.xml`, builds the product package, signs the installer, creates a DMG with resources and uninstall command, optionally calls `notarize.pl`, and writes md5/sha512 checksums.

## State And Persistence
Persistent outputs are `pkgroot`, `dpkgroot`, `plugins`, `OpenAFS-dist.pkg`, `OpenAFS-debug-extension.pkg`, `OpenAFS.pkg`, `OpenAFS-<version>-<relname>.dmg`, and checksum files in the working directory. It removes and recreates those trees on each pass. Installed package contents target `/Library/OpenAFS`, `/private/var/db/openafs`, LaunchDaemons, paths.d/manpaths.d, and either `/usr` or `/opt/openafs` symlink surfaces.

## Dependencies And Integration Points
It is the main macOS packaging orchestrator for resources such as `decode-panic`, `krb5-weak.conf`, `settings.plist`, `openafs.launchdaemon`, installer plugins, preference pane bundles, and `notarize.pl`. It integrates with OpenAFS `make dest` output, Apple Installer packaging, Gatekeeper signing/notarization, release CellServDB distribution, and macOS SIP-era filesystem layout differences.

## Risks And Test Signals
Risks include hard-coded Darwin version mappings, missing quoting in some command substitutions, signing order sensitivity, destructive cleanup of working directories, network dependency on central.org when `--csdb` is omitted, and fragile resource naming per macOS major version. Test signals include pass-1 package-root inspection, signature verification of every signed object, `pkgbuild`/`productbuild` success, correct Distribution OS bounds, notarization success, valid checksums, installation/uninstallation on supported macOS versions, and kext/debug package contents matching the source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/pkgbuild.sh.in -->
