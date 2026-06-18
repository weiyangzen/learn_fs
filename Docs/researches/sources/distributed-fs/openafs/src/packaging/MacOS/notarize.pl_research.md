<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/notarize.pl -->
# sources/distributed-fs/openafs/src/packaging/MacOS/notarize.pl

## Purpose
Automates Apple notarization for an OpenAFS macOS package image. It verifies prerequisites, submits a package to Apple's notary service with a named keychain profile, waits for acceptance, and staples the notarization ticket to the package.

## Important APIs, Types, And Functions
The Perl script uses `File::Which` and defines `usage`, `check_prerequisites`, `process_package`, `notarize_package`, and `main`. It requires root (`$> == 0`), `xcrun` in `PATH`, a valid notarytool keychain profile, and an existing package path. External commands are `xcrun notarytool history`, `xcrun notarytool submit --wait --timeout 5m`, and `xcrun stapler staple -v`.

## Control Flow
`main` requires exactly `<profile> <package>`. `check_prerequisites` exits with diagnostics if not run as root, `xcrun` is missing, notarytool cannot access the profile, or the package does not exist. `process_package` submits the package and extracts the first submission UUID from notarytool output. `notarize_package` staples the ticket and reports success, preserving the UUID in error messages.

## State And Persistence
The script does not store its own state. It reads Apple credentials from the named keychain profile and mutates the package by stapling notarization metadata. It emits status to stdout and errors to stderr.

## Dependencies And Integration Points
`pkgbuild.sh.in` calls this helper after creating the distribution DMG when a keychain profile is configured. It depends on current Xcode command-line tools, Apple's notary service, network access, and the certificate/keychain setup used by release builders.

## Risks And Test Signals
Risks include brittle UUID parsing from human-readable `notarytool` output, the fixed five-minute timeout, root-only execution despite notarytool often working as a user, and no retry/log fetch on rejection. Test signals include failure on missing profile/package, successful UUID extraction, stapler success, and an end-to-end package build where `spctl`/Gatekeeper validates the resulting DMG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/notarize.pl -->
