# subset-b-007789 Research

Grouped research for OpenAFS macOS, OpenBSD, RedHat packaging, PAM, AIX platform, and Darwin preference/backgrounder files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/decode-panic -->
# sources/distributed-fs/openafs/src/packaging/MacOS/decode-panic

## Purpose
Decodes macOS kernel panic logs that reference the OpenAFS kernel extension and produces a symbolized crash dump. It locates the latest complete panic section, extracts the OpenAFS load address, kernel version, slide, and backtrace addresses, prepares kext/kernel symbol files, drives `gdb`, and writes a readable dump under `/var/db/openafs/logs` by default.

## Important APIs, Types, And Functions
The script is Perl using `Getopt::Long`, `File::Temp`, `IO::File`, `File::Basename`, `Pod::Usage`, and `bigint`. Main helpers are `read_panic`, `extract_openafs`, `extract_kernel`, `generate_symbol_files`, `write_gdb_input_file`, and `write_dump_file`. External tools are `gdb`, `kextload` or `kextutil`, optional `dmgutil`/`hdutil`, `gzcat`, `pax`, and `cp`. Options select panic input, dump output, kernel image, system extension path, debug-kit archive, OpenAFS package archive, DMG utility, quiet/verbose modes, and help.

## Control Flow
Startup validates required programs and the panic file, parses crash metadata, maps the kernel version string to `gdb` and kext architectures, optionally extracts matching kernel/debug and OpenAFS kext artifacts from DMGs, generates symbol files at the adjusted OpenAFS load address, writes `gdb` commands that subtract the kernel slide from each backtrace address, runs `gdb -batch`, and writes the dump. `read_panic` seeks to the last panic section, supports older PPC and Intel backtrace formats, scans loaded or unloaded kext lists for `org.openafs.filesystems.afs`, and records a warning if the module was unloaded.

## State And Persistence
Temporary state lives under an auto-cleaned `afsdebugXXXXXX` directory. Persistent output is only the requested crash dump file; the script creates its parent directory if needed and clobbers the target file. It reads system panic logs, installed kexts, optional KDK/OpenAFS archives, and kernel files but does not modify them except for copying kexts into the temp area when `kextutil` needs that layout.

## Dependencies And Integration Points
This is a Mac packaging/support utility installed into the OpenAFS tools bundle by `pkgbuild.sh.in`. It integrates with Apple's kext symbol tooling, historical Darwin panic-log formats, OpenAFS installer archive layout, and OpenAFS kernel extension bundle paths. Its output helps correlate panic PCs with OpenAFS source lines.

## Risks And Test Signals
Risks include stale assumptions about `/mach_kernel`, `gdb`, legacy panic formats, regex parsing of version strings, shell backticks with globbed DMG paths, and failures when modern macOS lacks kextload/gdb behavior expected by the script. Test signals are successful decoding of sample PPC/Intel panic logs, correct kernel-slide subtraction, valid kext symbol loading for `kextload` and `kextutil`, useful failure in quiet/non-quiet modes, and non-empty dump output with panic date, kernel version, OpenAFS version, and disassembly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/decode-panic -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/krb5-weak.conf -->
# sources/distributed-fs/openafs/src/packaging/MacOS/krb5-weak.conf

## Purpose
Provides a minimal Kerberos configuration snippet for macOS packaging that enables weak cryptography. It is shipped into the OpenAFS private configuration area so legacy AFS/Kerberos workflows can still operate when they require older encryption types.

## Important APIs, Types, And Functions
The file is not executable code. It contains a `[libdefaults]` section with `allow_weak_crypto = true`, which is interpreted by MIT/Heimdal Kerberos libraries through normal krb5 configuration loading.

## Control Flow
There is no control flow in the file itself. `pkgbuild.sh.in` copies it into `private/var/db/openafs/etc/krb5-weak.conf` during package-root creation, where OpenAFS scripts or user instructions can point Kerberos tooling at it.

## State And Persistence
The persistent state is the installed config file. Enabling weak crypto affects processes that include this config in their krb5 configuration chain; it does not modify the system krb5 config directly.

## Dependencies And Integration Points
It depends on Kerberos libraries honoring `allow_weak_crypto`. It integrates with macOS installer packaging and legacy OpenAFS authentication paths that may still need DES/weak enctype compatibility.

## Risks And Test Signals
The explicit security risk is enabling weak cryptography. Packaging tests should verify the file is installed only where intended, while authentication tests should confirm legacy cells work when this config is used and modern Kerberos behavior remains unaffected when it is not referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/krb5-weak.conf -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/universal.sh -->
# sources/distributed-fs/openafs/src/packaging/MacOS/universal.sh

## Purpose
Creates a universal Darwin 8 destination tree by combining separate PowerPC and x86 OpenAFS build outputs. It copies both architecture trees into `u_darwin_80` and uses `lipo` to replace selected binaries with fat binaries.

## Important APIs, Types, And Functions
This is a small shell script using `tar`, `find`, `rm`, and `lipo`. It expects a top directory containing `ppc_darwin_80/dest` and `x86_darwin_80/dest`; `DIRLIST` identifies server binaries, client binaries, libraries, `afsd`, and the kext executable.

## Control Flow
The script validates that a top directory argument exists, resolves it and the current directory, creates `u_darwin_80`, overlays PPC and x86 trees with tar pipelines, then iterates every file found under each listed destination subpath. For each file it deletes the copied output and runs `lipo <ppc-file> <x86-file> -create -output <universal-file>`.

## State And Persistence
It creates or mutates `u_darwin_80` in the current directory and assumes that output name is free. It does not clean an existing output tree before `mkdir`, so reruns can fail or merge stale state.

## Dependencies And Integration Points
The script belongs to the historical macOS packaging path for Darwin 8/Tiger universal binaries. It depends on architecture-specific OpenAFS dest trees and Apple `lipo`.

## Risks And Test Signals
Risks include unquoted paths, hard-coded Darwin 8 architecture names, no validation that all files exist in both inputs, and broad file iteration that assumes every found file is a Mach-O object acceptable to `lipo`. Test signals include successful creation from clean PPC/x86 dest trees and `lipo -info` showing expected architectures for all binaries in `DIRLIST`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/MacOS/universal.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/OpenBSD/buildpkg.sh -->
# sources/distributed-fs/openafs/src/packaging/OpenBSD/buildpkg.sh

## Purpose
Builds a simple OpenBSD client tarball layout from an in-tree OpenAFS build. The header notes it no longer creates a native package; instead it assembles symlinks and configuration into `openafs-client.tgz`.

## Important APIs, Types, And Functions
The shell script uses `mkdir`, `chmod`, `ln -s`, `echo`, and `tar`. It links client/admin commands (`fs`, `klog`, `pagsh`, `pts`, `tokens`, `unlog`, `vos`, `bos`), `afsd`, `libafs.o`, `postinstall`, and `afs.rc.obsd` from relative source/build locations.

## Control Flow
It removes any existing `usr` staging tree, creates `usr/vice/bin`, `usr/vice/etc`, and `usr/vice/cache`, sets cache permissions to 700, creates symlinks to built artifacts, writes `cacheinfo`, and archives the staged `usr/vice` tree. The old `pkg_create` line is commented out.

## State And Persistence
Outputs are the local `usr` staging tree and `openafs-client.tgz`. The cacheinfo inside the tarball hard-codes `/afs:/usr/vice/cache:96000`.

## Dependencies And Integration Points
This integrates OpenAFS OpenBSD build outputs into a legacy client install payload. It depends on the relative `SRC=../../../../..` layout and on target artifacts already being built.

## Risks And Test Signals
Risks include stale symlinks in the tarball if target build products are missing, no error handling, destructive `rm -rf usr`, and no package metadata. Test signals are tarball contents, symlink targets resolving in the intended build/install environment, and a manual OpenBSD client install smoke test using the generated cacheinfo and rc script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/OpenBSD/buildpkg.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/makesrpm.pl -->
# sources/distributed-fs/openafs/src/packaging/RedHat/makesrpm.pl

## Purpose
Constructs an OpenAFS source RPM from a source tarball, release notes, ChangeLog, and CellServDB source. It derives RPM version/release metadata from the unpacked source, populates an rpmbuild tree, templates `openafs.spec.in`, builds an SRPM, and copies it to a requested output directory.

## Important APIs, Types, And Functions
The Perl script uses `Getopt::Long`, `Pod::Usage`, `IO::Dir`, `File::Path`, `File::Copy`, `File::Temp`, `File::Basename`, and `File::Spec`. Options are `--dir` and `--cellservdb-url`. External commands include `tar`, `build-tools/git-version`, `wget`, `sed`, `touch`, and `rpmbuild -bs`.

## Control Flow
It validates the source tarball, extracts only configure/version/build-tool/RedHat packaging paths into a tempdir, runs `git-version`, maps OpenAFS versions to RPM `Version`/`Release` rules for prerelease/dev/git-describe forms, creates `SPECS`, `SRPMS`, and `SOURCES`, copies packaging helpers except the spec template, obtains or overrides the CellServDB URL, copies a provided CellServDB or downloads it, installs release-note/changelog files or empty fallbacks, substitutes version macros and optional CellServDB source into the spec, builds the SRPM with modules disabled, and copies the single generated `.src.rpm` to `--dir`.

## State And Persistence
All build state is under a cleanup tempdir until the final SRPM is copied out. The final output directory is created if needed. No repository state is modified.

## Dependencies And Integration Points
It feeds the RedHat packaging pipeline by producing the SRPM consumed by `mockbuild.pl`, direct `rpmbuild`, or downstream maintainers. It depends on `openafs.spec.in` macros, the source archive layout, and the packaging helper files in `src/packaging/RedHat`.

## Risks And Test Signals
Risks include shell-string command construction with user-provided paths/URLs, reliance on bzip2 tarballs and `wget`, fragile extraction of the first tempdir entry, and sed quoting around version values. Test signals include correct RPM version/release for final, pre, dev, and git-describe source versions; CellServDB override behavior; exactly one SRPM generated; and `rpm -qip`/`rpmbuild --rebuild --define build_modules 0` sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/makesrpm.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/mockbuild.pl -->
# sources/distributed-fs/openafs/src/packaging/RedHat/mockbuild.pl

## Purpose
Mass-builds OpenAFS RPMs and kmod RPMs across multiple mock chroots and kernel-devel variants. It discovers available kernel packages, skips known-bad variants, builds missing userland packages and missing kmods, publishes result repositories, and stashes kernel-devel RPMs for later builds.

## Important APIs, Types, And Functions
The Perl script defines `findKernels`, `%platconf`, `%badkernels`, command-line options `--resultdir` and `--resultlist`, and uses external `mock`, `repoquery`, `rpm`, `setarch`, `createrepo`, and `cp`. `%platconf` maps CentOS/EPEL/Fedora mock configs to OS tags, base architectures, update repositories, and result paths.

## Control Flow
After parsing platforms and SRPM, it queries the SRPM version/release and decides whether the package uses `%dist`. For each selected platform it initializes the mock root, uses `findKernels` with mock yum config to gather `kernel-devel` providers, filters architecture/debug/bad/stale entries, builds userland RPMs if any expected outputs are missing, then loops every discovered arch/version/variant to build missing `kmod-openafs` packages. It copies outputs from the mock result directory, regenerates repository metadata, optionally stashes cached kernel-devel RPMs into a scratch repository, and writes a result list of new RPMs.

## State And Persistence
Persistent state includes result directories under `--resultdir`, optional `--resultlist`, repository metadata in each result directory, and stashed kernel-devel RPMs under the hard-coded scratch repository. Mock roots and caches under `/var/lib/mock` are initialized and reused.

## Dependencies And Integration Points
This is a release/build-farm helper for the SRPM generated by `makesrpm.pl` and the RPM spec's kmod build modes. It depends on mock config naming, yum/repoquery behavior, kernel-devel repository metadata, the OpenAFS RPM naming convention, and `openafs-kmodtool`/spec macros.

## Risks And Test Signals
Risks include hard-coded old platform lists, shell-string command construction, a stray `strace -o /tmp/out` in one repoquery path, mismatch for Fedora 17 result paths, race/staleness in result directories, and skipping newer releases when `ignorerelease` finds older kmods. Test signals include discovering kernels per mock config, building missing userland only once, building all needed kmod variants, valid `createrepo` output, and an accurate `--resultlist` of newly copied RPMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/mockbuild.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildall.sh -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildall.sh

## Purpose
Legacy helper to build OpenAFS RPMs and kernel modules for all installed kernel source trees on the current RedHat/SuSE-like host. It detects the OS flavor and running kernel series, builds the base package, then builds module packages for each local kernel source directory.

## Important APIs, Types, And Functions
The shell script uses `/etc/redhat-release` or `/etc/SuSE-release`, `uname`, `sed`, `grep`, `awk`, `ls`, and `rpmbuild`. Important variables are `specdir`, `buildopts`, `ostype`, `osrel`, `osvers`, `kbase`, `kv`, `archlist`, `kvers`, and `ksrcdir`.

## Control Flow
It maps release text to `fc`, `rhel`, `rh`, or `suse` tags and computes `osvers`. It classifies running kernels as 2.4 or 2.6, selects source-tree base paths, runs `rpmbuild -ba` for userspace/base packages, enumerates kernel source directories, ignores symlinks, derives variant names and target architectures, removes excluded architectures such as i586 on RHEL/CentOS, and runs `rpmbuild -bb` with `build_modules 1` for each kernel/arch pair.

## State And Persistence
Outputs are normal rpmbuild products in the system RPM build tree. The script reads system release files and kernel source directories but does not maintain internal state.

## Dependencies And Integration Points
It integrates directly with `/usr/src/redhat/SPECS/openafs.spec` or SuSE's `/usr/src/packages/SPECS` and predates the mock-based builder. It depends on local kernel source layout and the spec's `osvers`, `kernvers`, `ksrcdir`, and `build_modules` definitions.

## Risks And Test Signals
Risks include unquoted shell variables, very old OS/kernel assumptions, brittle release parsing, and building against every matching local kernel source tree. Test signals are correct `osvers` derivation, successful base rpmbuild, correct module variant naming for 2.4/2.6 kernels, and RPM outputs installable against the target kernel trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildall.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildfedora.pl -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildfedora.pl

## Purpose
Builds OpenAFS RPMs on Fedora systems using Fedora-style kmod variants discovered from installed `kernel*-devel` packages. It builds the base package once and then module packages for every discovered architecture/kernel/variant tuple.

## Important APIs, Types, And Functions
The Perl script uses `rpm -q fedora-release`, `rpm -q --queryformat` for `kernel`, `kernel-PAE`, `kernel-kdump`, and `kernel-xen` devel packages, `ls -d /usr/src/kernels/...`, and `rpmbuild`. It stores variants in a nested `%list` keyed by arch and version.

## Control Flow
It determines the Fedora version, iterates known variants, skips variants whose RPM query fails, parses package names into kernel version and architecture, discovers arch-specific kernel source directories, and records variant lists. It then runs `rpmbuild -ba` with `fedorakmod 1` and `osvers fc<version>`, followed by `rpmbuild -bb` for each arch/version with `build_modules 1`, `kernvers`, and `kvariants`.

## State And Persistence
The script writes only standard rpmbuild artifacts. Its state is the in-memory `%list` derived from installed kernel-devel packages and `/usr/src/kernels`.

## Dependencies And Integration Points
It integrates with the RedHat spec's Fedora kmod branch and expects `openafs.spec` in `/usr/src/redhat/SPECS`. It overlaps with but is simpler than `mockbuild.pl`.

## Risks And Test Signals
Risks include old Fedora variant assumptions, fragile regex parsing of kernel package names, reliance on local installed kernel-devel packages, and shell-string invocation of rpmbuild. Test signals include correct variant discovery for installed kernels and successful base plus kmod RPM builds for each recorded tuple.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildfedora.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client-systemd-helper.sh -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client-systemd-helper.sh

## Purpose
Implements the operational logic behind `openafs-client.service`. It starts the OpenAFS client, stops `/afs`, and performs post-stop cleanup in a way systemd can model while dealing with kernel-module and mount-state edge cases.

## Important APIs, Types, And Functions
The bash script accepts `ExecStart`, `ExecStop`, or `ExecStopPost`. It sources `/etc/sysconfig/openafs`, uses `fs sysname`, `sed`, `chmod`, `lsmod`, `rmmod`, `modprobe`, `/usr/vice/etc/afsd`, `umount`, `mountpoint`, `systemctl is-system-running`, and `sleep`. `UMOUNT_TIMEOUT` controls shutdown retry behavior.

## Control Flow
`ExecStart` first detects an already-running client via `fs sysname` and exits successfully to let systemd regain control. Otherwise it concatenates `CellServDB.local` and `.dist`, ensures permissions, removes a partially initialized loaded `openafs` module, loads the module, and execs `afsd` with configured args. `ExecStop` attempts to unmount `/afs`; during system shutdown it retries for up to 30 seconds if `/afs` remains a mountpoint. `ExecStopPost` runs `afsd -shutdown`, tries to unload the module, and emits explicit remediation instructions if the module remains loaded.

## State And Persistence
The helper rewrites `/usr/vice/etc/CellServDB`, loads/unloads the kernel module, starts/stops `afsd`, and changes the `/afs` mount state. It does not store separate state; it derives state from commands and systemd.

## Dependencies And Integration Points
It is installed by `openafs.spec.in` and referenced by `openafs-client.service`. It depends on OpenAFS client tools in legacy `/usr/vice/etc`, kernel module tooling, systemd state, and `/etc/sysconfig/openafs` for `AFSD_ARGS`.

## Risks And Test Signals
Risks include assuming `fs` is available in PATH, service activation when an old client is running, unmount races with active `/afs` users, and systemd considering the service inactive when module unload fails. Test signals include clean start from unloaded state, idempotent start when already running, stop during active `/afs` use, shutdown retry behavior, and accurate failure messaging when `rmmod` cannot unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client-systemd-helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client.service -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client.service

## Purpose
Defines the systemd unit for the OpenAFS client. It delegates lifecycle operations to `openafs-client-systemd-helper.sh` and arranges ordering relative to network and remote filesystem targets.

## Important APIs, Types, And Functions
The unit uses `Wants=network-online.target`, `After=syslog.target network-online.target dkms.service`, `Before=remote-fs.target`, `Type=forking`, `RemainAfterExit=true`, helper-backed `ExecStart`, `ExecStop`, and `ExecStopPost`, plus `KillMode=process`, `GuessMainPID=no`, `SendSIGKILL=no`, and `KillSignal=SIGCONT`.

## Control Flow
On start, systemd invokes the helper's `ExecStart`; the helper loads the module and starts `afsd`. On stop, systemd invokes helper `ExecStop` to unmount `/afs`, then always runs `ExecStopPost` to shut down afsd and unload the module. Installation enables the unit for both `multi-user.target` and `remote-fs.target`.

## State And Persistence
The unit stores no state itself. It models OpenAFS as remaining active after the start command exits and relies on mount/module state maintained by the helper and kernel.

## Dependencies And Integration Points
It is packaged by the RPM spec for systemd-capable Fedora/RHEL/Amazon systems. It integrates with DKMS ordering, network availability, remote-fs ordering, and the legacy `/usr/vice/etc` helper path.

## Risks And Test Signals
Risks include forking-service modeling without a tracked main PID, unusual `KillSignal=SIGCONT`, and inactive unit state when `/afs` remains mounted after failed stop. Test signals are `systemctl start/stop/status`, correct ordering at boot/shutdown, no forced kill of cache-manager processes, and clear journal output from the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-kmodtool -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-kmodtool

## Purpose
Generates RPM spec fragments and kernel-version metadata for OpenAFS kmod packages. It is a Fedora/RHEL-style kmodtool adapted for OpenAFS and emits `%package`, dependency, scriptlet, and file-list sections for one or more kernel variants.

## Important APIs, Types, And Functions
The bash script exposes commands `verrel`, `variant`, `rpmtemplate`, and `version`. Functions include `get_verrel`, `print_verrel`, `get_variant`, `print_variant`, `get_rpmtemplate`, and `print_rpmtemplate`. It uses extended glob patterns to strip known variants such as PAE, debug, smp, xen, kdump, and handles elrepo, EL, Fedora, RHEL, and Amazon version patterns.

## Control Flow
`verrel` normalizes a `uname -r` string to the version-release base used by build dependencies. `variant` subtracts that base to obtain the kernel variant suffix. `rpmtemplate` validates kmod name, kernel version, and depmod path, computes kernel dependency/provides naming for OS families, then prints RPM macro text for `kmod-openafs` packages, depmod post scripts, module file lists, and older debuginfo subpackages.

## State And Persistence
The script is stateless and writes generated spec text to stdout. The RPM spec consumes it through `%{expand:%(... rpmtemplate ...)}`.

## Dependencies And Integration Points
It is copied into SRPM sources by `makesrpm.pl` and invoked by `openafs.spec.in`. Its output must align with kernel package naming across Fedora/RHEL/Amazon and with where the spec installs `/lib/modules/<kname>/extra/openafs/openafs.ko`.

## Risks And Test Signals
Risks include kernel naming drift, brittle shell pattern handling for new distro releases, dependency epoch differences such as Amazon 2023, and mismatches between generated `%files` paths and install paths. Test signals include `openafs-kmodtool verrel/variant` on representative `uname -r` values and successful rpmbuild dependency resolution/install for standard and variant kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-kmodtool -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-makesrc.sh -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-makesrc.sh

## Purpose
Converts kernel RPMs into kernel source/build trees under `/usr/src/kernels` for older OpenAFS module build workflows. It extracts each RPM's embedded `lib/modules/*/build` directory and renames it to the convention expected by packaging scripts.

## Important APIs, Types, And Functions
The shell script uses `rpm -qp`, `rpm2cpio`, `cpio`, `sed`, `mkdir`, `chmod`, `rmdir`, and positional RPM arguments. It derives `vers`, `smp`, `arch`, and destination `kd=/usr/src/kernels/<vers><smp>-<arch>`.

## Control Flow
For each RPM argument it queries the package name, extracts the kernel version and variant prefix, derives architecture from the RPM filename, skips if the destination already exists, otherwise extracts `*lib/modules/*/build/*` into `/usr/src/kernels`, moves the build directory to the computed destination, fixes permissions, and removes empty intermediate directories.

## State And Persistence
It creates persistent kernel source directories under `/usr/src/kernels`. It also creates `/usr/src/kernels` if absent and removes temporary `lib/modules` extraction directories after a successful move.

## Dependencies And Integration Points
This supports `openafs-buildall.sh` and old RPM flows that expect local kernel build directories instead of `kernel-devel` packages. It depends on the structure of kernel RPM contents.

## Risks And Test Signals
Risks include root-owned system path mutation, fragile version/variant regexes, cleanup assumptions if extraction fails, and lack of quoting. Test signals include conversion of plain and SMP/PAE kernel RPMs, resulting build tree usability for rpmbuild, and no leftover `/usr/src/kernels/lib` directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-makesrc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-server.service -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-server.service

## Purpose
Defines the systemd unit for the OpenAFS server bosserver. It starts `bosserver` in the foreground and stops the local cell services through `bos shutdown`.

## Important APIs, Types, And Functions
The unit uses `EnvironmentFile=-/etc/sysconfig/openafs`, `ExecStart=/usr/afs/bin/bosserver -nofork $BOSSERVER_ARGS`, and `ExecStop=/usr/bin/bos shutdown localhost -wait -localauth`. It is ordered after `syslog.target` and `network.target` and installs into `multi-user.target`.

## Control Flow
Systemd starts `bosserver` directly and tracks it as the service process because `-nofork` keeps it in the foreground. Stop asks the local bosserver to shut down all managed services using local authentication and waits for completion.

## State And Persistence
The unit itself persists no state. It controls server processes and relies on OpenAFS server configuration under `/usr/afs` and arguments from `/etc/sysconfig/openafs`.

## Dependencies And Integration Points
It is installed by `openafs.spec.in` for systemd systems and replaces older SysV init handling. It integrates with bosserver, bos command-line tools, local server keys, and the RPM server package.

## Risks And Test Signals
Risks include failed stop if `bos` cannot authenticate locally or the server is partly broken, and only basic network ordering rather than stronger dependencies on configured storage. Test signals are `systemctl start/stop openafs-server`, foreground bosserver logging, successful `bos shutdown`, and daemon-reload behavior on package install/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-server.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs.spec.in -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs.spec.in

## Purpose
The primary RPM spec template for OpenAFS on Fedora, RHEL, CentOS, and Amazon Linux. It builds userspace packages, optional authentication libraries, Kerberos tools, legacy kauth packages, documentation, kernel-source and DKMS packages, and kernel-module RPMs across distro/kernel variants.

## Important APIs, Types, And Functions
Important macros include `afsvers`, `pkgvers`, `pkgrel`, `source_date_epoch`, `build_userspace`, `build_modules`, `build_dkmspkg`, `kauth_support`, `build_authlibs`, `krb5support`, `depmod`, `kmodtool`, `kverrel`, `kvariants`, `dkms_version`, `initdir`, and `pamdir`. Source entries include OpenAFS source, release notes, ChangeLog, CellServDB, build helpers, and `openafs-kmodtool`. It invokes `./configure`, `make only_libafs_tree`, `make all_nolibafs`, `make libafs`, `make install_nolibafs`, DKMS config generation, systemd/SysV script installation, and kmodtool-generated spec sections.

## Control Flow
The spec sets defaults unless overridden by rpmbuild definitions, declares subpackages, expands kmod package templates when module builds are enabled, unpacks the source, computes the OpenAFS sysname from target architecture, chooses kernel source paths, configures OpenAFS with transarc paths and optional krb5/swig/kauth features, builds the libafs tree, configures additional variant module trees, builds userspace and modules, installs userspace into `RPM_BUILD_ROOT`, prunes obsolete/duplicated files, relocates `afsd` and admin utilities, installs PAM modules when kauth is enabled, adds init/systemd files, creates client/server configuration directories, installs CellServDB.dist/cacheinfo/ThisCell, emits DKMS and kernel-source trees, installs docs, creates compatibility symlinks, installs kmods into `/lib/modules/.../extra/openafs`, then defines package scriptlets and file lists.

## State And Persistence
Build-time state includes `libafs_tree`, `_kmod_build_<variant>` directories, `RPM_BUILD_ROOT`, generated `dkms.conf`, generated `Distribution`-like package manifests, and installed module paths. Runtime package state includes `/etc/sysconfig/openafs`, `/usr/vice`, `/usr/afs`, `/afs`, CellServDB.local/dist/combined files, systemd or SysV service registrations, DKMS registrations, and depmod metadata.

## Dependencies And Integration Points
The spec is consumed by `makesrpm.pl`, `mockbuild.pl`, direct rpmbuild helpers, and distro packagers. It integrates with `openafs-kmodtool`, `openafs-client-systemd-helper.sh`, client/server unit files, legacy init scripts, OpenAFS configure/build targets, PAM, Kerberos, SWIG Perl bindings, DKMS, kernel-devel packages, systemd scriptlets, and central.org CellServDB distribution.

## Risks And Test Signals
Risks include macro drift across RPM versions/distros, kernel-source path naming changes, broad file-list fragility, package split conflicts, DKMS build failures, service scriptlet behavior on upgrade/removal, security implications of legacy kauth/PAM packaging, and hard-coded Source20 freshness. Test signals include SRPM creation, mock rebuilds with userspace-only and modules-only modes, install/upgrade/remove of every subpackage, DKMS add/build/install/remove, generated kmod dependency correctness, systemd/SysV service operation, `rpmlint` or distro policy review, and file-list completeness on all supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs.spec.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/Makefile.in -->
# sources/distributed-fs/openafs/src/pam/Makefile.in

## Purpose
Builds the OpenAFS PAM modules and a small PAM test program. It creates both `pam_afs.so` and `pam_afs.krb.so`, links them with OpenAFS authentication/token libraries, and installs them only when kauth installation is enabled.

## Important APIs, Types, And Functions
The makefile uses OpenAFS config, pthread, and libtool make fragments. Key objects are account, session, password, prompt/message helpers, OpenAFS RPC/auth/protection/kauth libraries, and `ktc.c`. Kerberos-flavored objects define `AFS_KERBEROS_ENV`. Targets are `all`, `pam_afs.la`, `pam_afs.krb.la`, `test_pam`, `install`, `dest`, and `clean`.

## Control Flow
The default target builds `test_pam`, `pam_afs.la`, and `pam_afs.krb.la`. The two module targets compile shared libtool modules with different auth/credential/util/ktc objects. `test_pam` uses platform-specific link lines. `install` and `dest` copy the resulting `.so` files into the configured lib directory or dest tree only when `INSTALL_KAUTH=yes`.

## State And Persistence
Build artifacts are libtool objects/modules and `test_pam`. Install state consists of PAM module shared objects in `${libdir}` or `${DEST}/lib`; RPM packaging later relocates them to the PAM security module directory.

## Dependencies And Integration Points
This is the build glue for the PAM hook implementations in the same directory and for the RPM kauth-client package. It depends on PAM headers/libs and many OpenAFS internal libraries.

## Risks And Test Signals
Risks include symbol/export mismatches, platform-specific PAM link flags, building deprecated kauth functionality, and install path differences between build and distro package expectations. Test signals include successful libtool module builds, exported `pam_sm_*` symbols, `test_pam` linking, and PAM stack smoke tests for auth/setcred/session/password flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_account.c -->
# sources/distributed-fs/openafs/src/pam/afs_account.c

## Purpose
Implements the PAM account-management hook for the OpenAFS PAM module. It currently accepts all account-management checks unconditionally.

## Important APIs, Types, And Functions
The only exported function is `pam_sm_acct_mgmt(pam_handle_t *pamh, int flags, int argc, const char **argv)`, returning `PAM_SUCCESS`. It includes PAM application/module headers and OpenAFS config headers.

## Control Flow
There is no option parsing or external call. PAM invokes the account hook and the module immediately reports success.

## State And Persistence
No state is read, written, or persisted.

## Dependencies And Integration Points
The function is exported by the PAM modules built in `Makefile.in` and appears in the module export map. It lets OpenAFS participate in PAM account stacks without imposing account restrictions.

## Risks And Test Signals
The risk is policy ambiguity: account expiry/access checks must come from other PAM modules because this one never rejects. Test signals are compile/export coverage and PAM stack behavior where account management succeeds after authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_account.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_auth.c -->
# sources/distributed-fs/openafs/src/pam/afs_auth.c

## Purpose
Implements `pam_sm_authenticate` for legacy AFS/KA authentication. It validates an AFS password, optionally obtains tokens during authentication for applications that do not call `pam_setcred`, creates PAGs, supports `klog` fallback, and stores the password in PAM data for later credential establishment.

## Important APIs, Types, And Functions
The function uses PAM APIs (`pam_get_user`, `pam_get_item`, `pam_set_item`, `pam_set_data`), OpenAFS calls (`setpag`, `ktc_newpag`, `ktc_ForgetAllTokens`, `ka_VerifyUserPassword`, `ka_UserAuthenticateGeneral`), helper calls (`pam_afs_prompt`, `pam_afs_syslog`, `do_klog`, `lc_cleanup`), and platform-specific `getpwnam`/`getpwnam_r`. Options include `debug`, `nowarn`, `use_first_pass`, `try_first_pass`, `ignore_root`, `ignore_uid <n>`, `cell <name>`, `refresh_token`, `set_token`, `dont_fork`, `use_klog`, and accepted `setenv_password_expires`.

## Control Flow
The hook parses options, gets a PAM conversation and user, optionally ignores low-UID users, retrieves `PAM_AUTHTOK` or prompts for a password, rejects empty passwords, creates a PAG unless refreshing, and authenticates. By default it forks so KA library state/sockets are cleaned up in the child; `dont_fork` authenticates inline, while `use_klog` runs the external `klog`/`klog.krb` helper. If `try_first_pass` fails it reprompts. On success it returns `PAM_SUCCESS`; `KANOENT` maps to `PAM_USER_UNKNOWN`; other failures map to `PAM_AUTH_ERR`.

## State And Persistence
The module stores a duplicate password under `pam_afs_lh` with cleanup that zeros it on PAM end, may set `PAM_AUTHTOK`, creates a PAG in the process, and may obtain AFS tokens when `refresh_token` or `set_token` is used. Prompted passwords are copied into fixed 256-byte stack buffers and wiped before exit when owned.

## Dependencies And Integration Points
It is the authentication half of `pam_afs.so`/`pam_afs.krb.so` and feeds `afs_setcred.c` through PAM data. It integrates with KA servers, optional Kerberos-klog behavior, syslog, PAM conversation callbacks, and platform NSS.

## Risks And Test Signals
Risks include legacy KA security, fixed-size password buffer truncation, broad use of syslog around auth failures, fork/signal-handler interactions, retained password material in PAM data, and option conflict handling. Test signals include `use_first_pass`/`try_first_pass`/prompt flows, ignored UID behavior, alternate cell auth, token/PAG creation, `dont_fork` and `use_klog` modes, `KANOENT` user mapping, and password cleanup under `pam_end`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_auth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.c -->
# sources/distributed-fs/openafs/src/pam/afs_message.c

## Purpose
Provides the fallback message catalog and syslog formatter for the OpenAFS PAM module. It maps numeric `PAMAFS_*` message IDs to format strings used by auth, setcred, session, password, and prompt helpers.

## Important APIs, Types, And Functions
The file defines `fallback_messages`, `num_fallbacks`, `pam_afs_message(int msgnum, int *freeit)`, and `pam_afs_syslog(int priority, int msgid, ...)`. It uses `vsyslog`, varargs, and message constants from `afs_message.h`.

## Control Flow
`pam_afs_message` bounds-checks the message ID, falls back to index 0 for invalid values, and reports that the returned string must not be freed. `pam_afs_syslog` obtains the format string, formats varargs into syslog, and frees only if a future catalog-backed implementation requests it.

## State And Persistence
The message table is static process state. The only external side effect is syslog output.

## Dependencies And Integration Points
Every PAM source file uses these messages for consistent diagnostics and prompts through `afs_pam_msg.c`. The placeholder comment indicates this could be replaced by an NLS catalog later.

## Risks And Test Signals
Risks include format-string/signature mismatches between message IDs and callers, an apparent missing comma between message 46 and 47 strings causing concatenation, and no localization despite the abstraction. Test signals include compile warnings, exercising each message ID with representative arguments, and checking syslog output for malformed combined messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.h -->
# sources/distributed-fs/openafs/src/pam/afs_message.h

## Purpose
Declares numeric message IDs and public message/syslog functions for the OpenAFS PAM module.

## Important APIs, Types, And Functions
The header defines `PAMAFS_UNKNOWNOPT` through `PAMAFS_OTHERCELL`, matching the fallback table in `afs_message.c`, and declares `pam_afs_message` and `pam_afs_syslog`.

## Control Flow
There is no runtime control flow. Consumers pass constants to message, prompt, and syslog helpers instead of hard-coded strings.

## State And Persistence
No state is stored in the header. It defines the compile-time contract for message lookup.

## Dependencies And Integration Points
It is included by all PAM implementation files and must remain aligned with `fallback_messages` indices.

## Risks And Test Signals
The main risk is drift between constants and the message array, especially because varargs callers depend on exact format placeholders. Test signals are compile coverage and runtime log/prompt checks for each defined ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.c -->
# sources/distributed-fs/openafs/src/pam/afs_pam_msg.c

## Purpose
Wraps PAM conversation callbacks for displaying informational/error messages and prompting for passwords or other user input using OpenAFS message IDs.

## Important APIs, Types, And Functions
Functions are `pam_afs_printf` and `pam_afs_prompt`. Both call `pam_afs_message`, format varargs into a `PAM_MAX_MSG_SIZE` stack buffer, construct a `struct pam_message`, invoke `pam_conv->conv`, and clean returned `struct pam_response` storage.

## Control Flow
`pam_afs_printf` emits one `PAM_ERROR_MSG` or `PAM_TEXT_INFO` and frees any returned response. `pam_afs_prompt` emits one echo-on or echo-off prompt, returns the response string to the caller, and frees only the response container. Both return `PAM_CONV_ERR` if no valid conversation exists.

## State And Persistence
The helpers store no persistent state. `pam_afs_prompt` transfers ownership of the response string to the caller, which is expected to wipe/free password responses.

## Dependencies And Integration Points
Authentication, setcred, and password-change code use these helpers to prompt consistently through the application-provided PAM conversation.

## Risks And Test Signals
Risks include `vsprintf` into a fixed buffer, no check that the conversation returned a response for prompts, and ownership mistakes around sensitive responses. Test signals include prompt success/failure paths, echo-on/off behavior, oversized formatted messages, and valgrind/ASan checks for response cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.h -->
# sources/distributed-fs/openafs/src/pam/afs_pam_msg.h

## Purpose
Declares the PAM conversation helper functions used by the OpenAFS PAM module.

## Important APIs, Types, And Functions
The header declares `pam_afs_printf(PAM_CONST struct pam_conv *, int error, int fmt_msgid, ...)` and `pam_afs_prompt(PAM_CONST struct pam_conv *, char **response, int echo, int fmt_msgid, ...)`.

## Control Flow
There is no implementation control flow. The declarations define the shared interface for message display and prompting.

## State And Persistence
No state is stored by this header.

## Dependencies And Integration Points
It depends on PAM types from included callers and pairs with `afs_pam_msg.c`; auth, setcred, and password-change files include it.

## Risks And Test Signals
Risks are declaration drift and missing PAM type definitions in unusual include orders. Test signals are clean compilation of all PAM modules and prompt calls linking against `afs_pam_msg.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_pam_msg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_password.c -->
# sources/distributed-fs/openafs/src/pam/afs_password.c

## Purpose
Implements `pam_sm_chauthtok` for changing a user's legacy AFS/KA password. It verifies the old password, prompts for a new password twice, obtains an admin token, connects to the KA maintenance service, and submits the password change.

## Important APIs, Types, And Functions
The hook uses PAM APIs (`pam_get_user`, `pam_get_item`, `pam_set_item`), OpenAFS KA/RX APIs (`ka_VerifyUserPassword`, `ka_Init`, `rx_Init`, `ka_LocalCell`, `ka_StringToKey`, `ka_GetAdminToken`, `ka_AuthServerConn`, `ka_ChangePassword`), `ktc` token/key structs, message/prompt helpers, and NSS lookup. Options include `debug`, `nowarn`, `use_first_pass`, `try_first_pass`, and `ignore_root`.

## Control Flow
The function parses options, obtains conversation and user, optionally ignores root, gets or prompts for the old password, verifies it with `KA_USERAUTH_DOSETPAG`, saves it as `PAM_AUTHTOK`/`PAM_OLDAUTHTOK`, returns success immediately for `PAM_PRELIM_CHECK`, requires `PAM_UPDATE_AUTHTOK` for the update phase, prompts for and confirms a non-empty new password, initializes KA/RX, resolves the local cell, derives old/new keys, gets a short admin token, connects to the KA maintenance service, and calls `ka_ChangePassword`.

## State And Persistence
Successful execution changes the user's AFS password in the KA database and updates `PAM_AUTHTOK` to the new password. Old and new password buffers are partially wiped on error paths; prompted strings are owned by PAM conversation allocation.

## Dependencies And Integration Points
This is exported by the PAM module for password stacks and depends on legacy kaserver infrastructure. It integrates with the same message/prompt utilities as authentication and with KA maintenance RPCs.

## Risks And Test Signals
Risks include deprecated KA password handling, fixed 256-byte buffers for passwords/realm/cell, incomplete wiping/freeing of new password on success, password quality delegated elsewhere, and lack of alternate-cell option support despite auth/setcred supporting it. Test signals include prelim/update PAM phases, wrong old password, mismatched new passwords, KA server unavailability, successful password change, and PAM_AUTHTOK update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_password.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_session.c -->
# sources/distributed-fs/openafs/src/pam/afs_session.c

## Purpose
Implements PAM session hooks for OpenAFS token cleanup. Opening a session is a no-op; closing a session optionally destroys tokens immediately or after a delay.

## Important APIs, Types, And Functions
Exports `pam_sm_open_session` and `pam_sm_close_session`. Close-session options are `debug`, `remain`, `remainlifetime <seconds>`, and `no_unlog`. It uses `fork`, `setsid`, `sleep`, `ktc_ForgetAllTokens`, syslog, and `pam_afs_syslog`.

## Control Flow
`pam_sm_open_session` returns success. `pam_sm_close_session` parses options, and if `remain` is set without `no_unlog`, forks a detached child that closes file descriptors, sleeps for the configured lifetime, then forgets tokens; the parent logs session closed and returns success. Without delayed cleanup, it calls `ktc_ForgetAllTokens` immediately unless `no_unlog` is set.

## State And Persistence
The only persistent effect is deletion of AFS tokens from the current PAG/token context. Delayed cleanup creates a short-lived child process with no retained PAM state.

## Dependencies And Integration Points
This hook complements auth/setcred token establishment and is included in `pam_afs` exports. It relies on OpenAFS token cache semantics and syslog.

## Risks And Test Signals
Risks include token cleanup affecting shared PAGs, delayed child process behavior during logout, weak parsing of missing `remainlifetime` argument, and closing only descriptors 0-63. Test signals include immediate and delayed `unlog` behavior, `no_unlog`, invalid lifetime handling, and session close under Linux and non-Linux process-group semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_setcred.c -->
# sources/distributed-fs/openafs/src/pam/afs_setcred.c

## Purpose
Implements `pam_sm_setcred` for establishing or refreshing AFS credentials after successful authentication. It retrieves the password saved by `pam_sm_authenticate`, ensures a PAG exists, obtains or refreshes tokens, and optionally exports password-expiry and Kerberos ticket-file environment variables.

## Important APIs, Types, And Functions
The hook uses PAM APIs (`pam_get_user`, `pam_get_item`, `pam_get_data`, `pam_putenv`), OpenAFS APIs (`setpag`, `ktc_newpag`, `getPAG`, `ka_VerifyUserPassword`, `ka_UserAuthenticateGeneral`, `ktc_ForgetAllTokens`), optional Kerberos `ktc_tkt_string`, helper `do_klog`, and message/prompt utilities. It handles PAM flags `PAM_DELETE_CRED`, `PAM_REINITIALIZE_CRED`, `PAM_REFRESH_CRED`, and `PAM_ESTABLISH_CRED`.

## Control Flow
Options are parsed similarly to auth, including `cell`, `ignore_uid`, `refresh_token`, `use_klog`, and `setenv_password_expires`. Delete and reinitialize requests currently return success without modifying tokens. Establish/refresh retrieves the stored password or prompts if allowed, creates a PAG if not refreshing and none exists, verifies for refresh or obtains tokens for establish using either KA calls or external `klog`, supports retry after first-pass failure, then on success may set `PASSWORD_EXPIRES` and `KRBTKFILE`.

## State And Persistence
Successful establish/refresh creates AFS tokens in the current PAG. It may create a new PAG, set PAM environment variables, and chown a Kerberos ticket file to the local user's uid/gid in Kerberos builds. It wipes only locally copied prompt passwords.

## Dependencies And Integration Points
This is the credential half of the PAM module and depends on `afs_auth.c` storing the password under `pam_afs_lh`. It integrates with KA servers, optional `klog`, Kerberos ticket handling, and PAM session/application environment propagation.

## Risks And Test Signals
Risks include returning success for delete/reinitialize without token deletion, password retention through PAM data, fixed-size buffers, duplicate option parsing, and inconsistent behavior between KA and klog modes. Test signals include establish vs refresh flows, missing saved password, alternate cell, ignored UIDs, PAG creation only when needed, `PASSWORD_EXPIRES` and `KRBTKFILE` environment setting, and token presence after login.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_setcred.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.c -->
# sources/distributed-fs/openafs/src/pam/afs_util.c

## Purpose
Provides shared utility state and helper functions for the OpenAFS PAM module: secure cleanup callbacks, integer-to-string conversion, external `klog` execution, and current PAG lookup.

## Important APIs, Types, And Functions
Globals are `pam_afs_ident` and `pam_afs_lh`. Functions are `lc_cleanup`, `nil_cleanup`, `cv2string`, `do_klog`, and `getPAG`. `do_klog` chooses `KLOG` or `KLOGKRB`, builds `klog` arguments including optional cell and lifetime, pipes the password to the child process, and returns the child exit status. `getPAG` uses `ktc_curpag` and masks the low 24 bits.

## Control Flow
Cleanup callbacks zero/free or ignore PAM data. `do_klog` validates executable access, creates a pipe, forks, wires child stdin/stdout to the pipe, execs klog, writes password plus newline from the parent, closes descriptors, waits, and reports the exit code. `getPAG` maps invalid/current-none PAG values to `-1`.

## State And Persistence
The file defines process-global strings used as syslog identity and PAM data key. `do_klog` can create AFS/Kerberos tokens through the external command as a side effect. `lc_cleanup` erases password data when PAM ends.

## Dependencies And Integration Points
Auth and setcred call these helpers. The file depends on OpenAFS auth/ktc APIs, PAM types, syslog, process control, and hard-coded legacy paths `/usr/afsws/bin/klog`, `klog.krb`, and `unlog`.

## Risks And Test Signals
Risks include hard-coded executable paths, pipe descriptor handling that connects stdout to the same pipe, password exposure through external process I/O, wait behavior returning success on unexpected pid mismatch, and no close-on-exec discipline. Test signals include cleanup wiping, `do_klog` success/failure with fake helpers, alternate cell/lifetime arguments, and `getPAG` values before/after `setpag`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.h -->
# sources/distributed-fs/openafs/src/pam/afs_util.h

## Purpose
Declares shared utility globals, cleanup callbacks, klog/PAG helpers, and compatibility macros for the OpenAFS PAM module.

## Important APIs, Types, And Functions
Declarations include `pam_afs_ident`, `pam_afs_lh`, `lc_cleanup`, `nil_cleanup`, `cv2string`, `do_klog`, and `getPAG`. Constants define `KLOG`, `KLOGKRB`, `UNLOG`, and `IGNORE_MAX`. HPUX compatibility maps some PAM/syslog APIs.

## Control Flow
The header contains no runtime flow. It provides compile-time contracts and platform shims used by the PAM implementation files.

## State And Persistence
No state is stored here beyond externally defined global names and path constants.

## Dependencies And Integration Points
It is included by all major PAM files and ties option parsing (`IGNORE_MAX`) and external helper execution paths together.

## Risks And Test Signals
Risks include obsolete `/usr/afsws` paths, platform macro drift, and globals declared as mutable `char *`. Test signals are clean builds across supported PAM platforms and correct helper path usage in installed packages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/test_pam.c -->
# sources/distributed-fs/openafs/src/pam/test_pam.c

## Purpose
Provides a standalone interactive test driver for PAM stacks using the `afstest` service. It authenticates a named user, optionally establishes credentials, opens a session, then launches a shell for manual inspection.

## Important APIs, Types, And Functions
The program uses `pam_start`, `pam_authenticate`, `pam_acct_mgmt`, `pam_setcred`, `pam_open_session`, `pam_end`, a custom `my_conv` PAM conversation, `getpass`/`getpassphrase`, `putenv`, `chdir`, and `execl`. Option `-u` disables `pam_setcred`.

## Control Flow
`main` parses `[-u] <user>`, starts PAM for service `afstest`, authenticates, runs account management, optionally establishes credentials, opens a session, ends PAM, sets test environment variables, changes to `/tmp`, and execs `/bin/csh`. `my_conv` handles echo-off password prompts, echo-on input, error messages, and text info by allocating response arrays and reading from terminal/stdin.

## State And Persistence
The program starts a PAM transaction and may create credentials/tokens depending on the configured stack. It sets process environment variables and replaces itself with a shell; it does not write files.

## Dependencies And Integration Points
It is built by `Makefile.in` for PAM module testing and depends on a system PAM service named `afstest`. It exercises the OpenAFS module through the normal PAM API rather than direct calls.

## Risks And Test Signals
Risks include hard-coded `/bin/csh`, use of `getpass`, manual-only behavior, and limited cleanup after opening sessions because it calls `pam_end` before launching the shell rather than testing close-session. Test signals include successful auth/setcred/open-session, expected token visibility inside the shell, `-u` behavior without credentials, and conversation handling for prompt/message styles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/test_pam.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/AIX/Makefile.in -->
# sources/distributed-fs/openafs/src/platform/AIX/Makefile.in

## Purpose
Placeholder platform makefile for AIX-specific OpenAFS build hooks. It explicitly declares that there is no platform-specific work for AIX in this directory yet.

## Important APIs, Types, And Functions
The makefile defines `SHELL=/bin/sh` and empty `all`, `install`, `dest`, and `clean` targets.

## Control Flow
All targets are no-ops and return success.

## State And Persistence
No build artifacts, installed files, or cleanup state are produced by this makefile.

## Dependencies And Integration Points
It satisfies the platform directory build interface expected by the wider OpenAFS make system.

## Risks And Test Signals
The main risk is false confidence: AIX-specific requirements must be implemented elsewhere. Test signals are that recursive builds invoking these targets succeed without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/AIX/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.h

## Purpose
Declares the application delegate for the modern macOS OpenAFS backgrounder menu-bar app. The delegate owns the status menu, token/AFS state, preferences, timers, credential window, link creation state, and action methods for starting/stopping AFS and obtaining/releasing tokens.

## Important APIs, Types, And Functions
The interface imports Cocoa and `AFSMenuCredentialContoller`. It exposes `applicationDidFinishLaunching`/termination-related behavior through the implementation, timer controls, preference reading, token operations, status updates, Kerberos renewal, notification handlers, link-mode updates, status-item accessors, and menu action methods. Important ivars include `backgrounderMenu`, `startStopMenuItem`, `getReleaseTokenMenuItem`, `NSStatusItem *statusItem`, `AFSPropertyManager *afsMngr`, preference `NSNumber`s, `NSTimer`s, `NSLock`s, token state booleans, images, credential controller, and link configuration.

## Control Flow
The header defines the object surface used by the app nib and `AFSMenuExtraView`. The implementation initializes the delegate, reads preferences, starts timers, receives distributed/workspace notifications, updates status, and delegates menu drawing/actions through these declarations.

## State And Persistence
The delegate maintains in-memory menu/timer/lock/status state and reads persistent CFPreferences for OpenAFS preference keys. It also tracks user-configured desktop symlink mappings.

## Dependencies And Integration Points
It connects the `AFSBackgrounder` app nib to `AFSPropertyManager`, `Krb5Util`, distributed notifications shared with the preference pane, and the custom status-item view.

## Risks And Test Signals
Risks include manual memory management ownership, duplicated `imageToRender` declaration, timer/lock lifecycle mistakes, and preference values assumed non-null. Test signals are successful nib outlet/action binding, status item visibility changes, token refresh timer behavior, and clean app termination without leaked observers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.m

## Purpose
Implements the modern macOS OpenAFS backgrounder menu-bar app. It monitors AFS and token state, displays a status item, starts/stops AFS with authorization, gets/releases tokens, optionally renews Kerberos tickets, creates/removes desktop symlinks from preferences, and synchronizes with the preference pane through notifications.

## Important APIs, Types, And Functions
Key methods include `applicationDidFinishLaunching`, `applicationShouldTerminate`, `readPreferenceFile:`, `updateLinkModeStatusWithpreferenceStatus:`, `performLinkOpeartionOnThread:`, `chageMenuVisibility:`, `switchHandler:`, `afsVolumeMountChange:`, `klogUserEven:`, `startStopAfs:`, `getToken:`, `releaseToken:`, `updateAfsStatus:`, timer start/stop methods, `krb5RenewAction:`, `menuNeedsUpdate:`, `useAklogPrefValue`, `setStatusItem:`, `imageToRender`, and menu IBAction wrappers. It uses `AFSPropertyManager`, `AuthUtil`, `Krb5Util`, `AFSMenuExtraView`, `AFSMenuCredentialContoller`, CFPreferences, `NSDistributedNotificationCenter`, and `NSWorkspace` notifications.

## Control Flow
Launch allocates locks/managers/images, reads preferences, starts token-status polling, registers for preference/state/menu/mount/session notifications, creates the status item if configured, and optionally gets a token at login. Preference reload synchronizes CFPreferences, reads aklog/menu/login/link/Kerberos-renew settings, updates link mode on a detached thread, refreshes status, and restarts the renewal timer. Menu actions authorize and call `startup`/`shutdown`, run `getTokens` directly for aklog mode or display a credential window for password mode, or call `unlog`. Status refresh loads configuration, checks AFS status, reads token list, updates flags, and redraws the menu view.

## State And Persistence
Persistent inputs are CFPreferences under `kAfsCommanderID`, OpenAFS configuration under `/var/db/openafs`, token state, Kerberos tickets, and desktop symlink preferences. Runtime state includes timers, locks, status item/view, images, `afsState`, `gotToken`, `currentLinkActivationStatus`, and credential windows. Side effects include start/stop of OpenAFS services, token creation/destruction, Kerberos ticket renewal, and desktop symlink creation/removal.

## Dependencies And Integration Points
This app is packaged inside the preference pane/resources and communicates with AFSCommander via distributed notifications such as preference changes, menu events, token operations, and AFS state changes. It depends on the broader Darwin preference code for `AFSPropertyManager`, `TaskUtil`, `AuthUtil`, and `Krb5Util`.

## Risks And Test Signals
Risks include non-retained/copy preference objects leaking or becoming nil, a logic bug in link cleanup that checks `!linkSourcePathExist` inside an `else` where it is known true, UI work and file operations on detached threads, exception swallowing in Kerberos renewal, and manual observer/memory lifecycle hazards. Test signals include launch/quit observer cleanup, status item show/hide, menu title changes, token auto-acquisition on login/session switch, symlink creation/removal, Kerberos renewal timer firing, and start/stop authorization failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSBackgrounderDelegate.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.h

## Purpose
Declares a controller object for the backgrounder credential popover/window. It owns the view rectangle, credential view/window/controller outlets, and an `AFSPropertyManager` used to obtain tokens after the user submits credentials.

## Important APIs, Types, And Functions
The interface imports Cocoa, `CredentialWindowController`, and `AFSPropertyManager`. Public methods are `initWhitRec:afsPropManager:`, `showWindow`, and `closeWindow`.

## Control Flow
Callers initialize it with the menu/status-item rectangle and property manager, call `showWindow` to load and display the credential UI, and call `closeWindow` in response to the credential-window notification so it can either obtain tokens or dismiss.

## State And Persistence
It retains an `AFSPropertyManager`, references the credential window/view/controller, and stores the source rectangle. Persistent token changes occur only through the implementation's call to `getTokens`.

## Dependencies And Integration Points
It is used by `AFSBackgrounderDelegate` and the older `AFSMenuExtra` path when aklog mode is disabled. It depends on `CredentialWindow.nib` outlet wiring and `CredentialWindowController`.

## Risks And Test Signals
Risks include manual memory management, the misspelled initializer name being part of the call contract, and weakly typed `id` outlets. Test signals are nib loading, window placement, submit/cancel notification handling, and token acquisition with provided credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.m

## Purpose
Implements the backgrounder credential window wrapper. It loads the credential nib, displays an `NSWindow` near the status item, and on close obtains tokens with the username/password captured by `CredentialWindowController`.

## Important APIs, Types, And Functions
Methods are `initWhitRec:afsPropManager:`, `dealloc`, `showWindow`, and `closeWindow`. It uses `NSBundle loadNibNamed`, `NSWindow initWithContentRect`, `setFrameTopLeftPoint`, `makeKeyAndOrderFront`, and `AFSPropertyManager getTokens:true usr:pwd:`.

## Control Flow
Initialization stores the display rectangle and retains the property manager. `showWindow` computes a top-left point near the menu bar, loads `CredentialWindow.nib`, creates a titled window with the loaded credential view, and shows it. `closeWindow` checks whether the credential controller reports `takenToken`; if so it calls `getTokens` with the captured username/password, releases the property manager, then closes and clears the window.

## State And Persistence
Runtime state includes the credential window and retained property manager. The persistent/externally visible side effect is token creation through OpenAFS tools if the user submitted credentials.

## Dependencies And Integration Points
It integrates the credential nib/controller with both backgrounder menu implementations and with `AFSPropertyManager` token acquisition.

## Risks And Test Signals
Risks include not releasing `afsPropMngr` on cancel, using deprecated `loadNibNamed`, window/view ownership ambiguity, storing password strings without copying/wiping, and hard-coded positioning. Test signals include submit/cancel flows, no leaked observers/controllers after close, token acquisition with valid credentials, and behavior when the nib fails to load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuCredentialContoller.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.h

## Purpose
Declares the older SystemUIServer `NSMenuExtra` plugin implementation for OpenAFS. It predates or coexists with the standalone backgrounder app and provides a menu extra with AFS state, token state, login/unlog controls, and a custom view.

## Important APIs, Types, And Functions
The interface subclasses `NSMenuExtra` from `SystemUIPlugin.h`, imports global constants and the credential controller, and declares timer, preference, token, menu, image, and mount-change methods. Ivars track `afsState`, `gotToken`, `afsSysPath`, `useAklogPrefValue`, menu/menu-items, `AFSMenuExtraView`, token-state images, credential controller, timer, and lock.

## Control Flow
The implementation initializes the menu extra from a bundle, reads preferences, polls status, displays menu items, responds to token operations, and redraws its custom view through methods declared here.

## State And Persistence
The class stores in-memory menu/view/timer/lock state and reads user preferences for aklog behavior. It causes token side effects through `AFSPropertyManager`.

## Dependencies And Integration Points
It depends on the private/deprecated MenuExtra plugin API, custom `AFSMenuExtraView`, distributed notifications with the preference pane, and workspace mount notifications.

## Risks And Test Signals
Risks include private API compatibility, manual memory management, and overlap with the newer `AFSBackgrounderDelegate`. Test signals are plugin loading/unloading in supported macOS versions, menu item enablement, icon updates, and token operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.m

## Purpose
Implements the older OpenAFS SystemUIServer menu extra. It creates a custom menu/view, polls AFS/token state, reacts to preference and mount notifications, gets/releases tokens, and informs the preference pane when token operations occur.

## Important APIs, Types, And Functions
Key methods are `initWithBundle:`, `willUnload`, `startTimer`, `stopTimer`, `dealloc`, `menu`, `readPreferenceFile:`, `getToken:`, `releaseToken:`, `afsVolumeMountChange:`, `updateAfsStatus:`, `klogUserEven:`, `getImageFromBundle:fileExt:`, `imageToRender`, `updateMenu`, and `useAklogPrefValue`. It uses `NSMenuExtra`, `NSMenu`, `AFSMenuExtraView`, `AFSPropertyManager`, `AFSMenuCredentialContoller`, distributed notifications, workspace mount notifications, and token-state images.

## Control Flow
Initialization creates locks and a custom view, loads images, constructs menu items for start/stop/login/unlog, registers for preference/state/mount notifications, reads preferences, and starts a periodic token-status timer. `getToken:` either calls `getTokens` directly when aklog is enabled or opens the credential window and waits for its close notification. `updateAfsStatus:` lock-guards AFS status and token-list reads, updates menu titles/enabled state, and redraws the view. Unload/ dealloc invalidates timers and removes observers.

## State And Persistence
Runtime state includes menu objects, timer, lock, images, token/AFS booleans, and credential controller. Persistent effects are token creation/destruction through `AFSPropertyManager`; preferences are read through CFPreferences/NSUserDefaults.

## Dependencies And Integration Points
This code is tied to the old `SystemUIPlugin`/MenuExtra path and shares constants/notifications with the preference pane. It relies on `AFSPropertyManager` for actual OpenAFS operations and on `CredentialWindow.nib` for password-based login.

## Risks And Test Signals
Risks include private API breakage, inconsistent constant names (`afsCommanderID` vs `kAfsCommanderID`), assigning a BOOL result into an `NSNumber *` before replacing it, releasing an `AFSPropertyManager` while a credential controller may retain/use it, and manual observer cleanup. Test signals include menu extra load/unload, preference changes, mount notification refresh, aklog and manual credential flows, and no crashes when toggling the menu repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtra.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.h

## Purpose
Declares the custom status-item view used by the backgrounder menu. It draws the OpenAFS token-state icon, optional Kerberos indicator, and handles mouse/menu delegate events for a status item menu.

## Important APIs, Types, And Functions
The class subclasses `NSView` and conforms to `NSMenuDelegate`. It stores an `AFSBackgrounderDelegate`, `NSStatusItem`, `NSMenu`, and menu visibility flag. Methods include `initWithFrame:backgrounder:menu:`, `makeKerberosIndicator:`, `mouseDown:`, `menuWillOpen:`, `menuDidClose:`, and `menuNeedsUpdate:`.

## Control Flow
The view is initialized by `AFSBackgrounderDelegate` when a status item is shown. Mouse down opens the status item menu; menu delegate callbacks update highlighting and forward menu-update requests back to the delegate.

## State And Persistence
Only transient UI state is stored: status item/menu references and whether the menu is open. There is no persistent storage.

## Dependencies And Integration Points
It depends on `AFSBackgrounderDelegate` for token image selection and aklog preference, and on Cocoa status-item drawing APIs.

## Risks And Test Signals
Risks include deprecated drawing APIs and assuming `[backgrounderDelegator statusItem]` is valid during initialization. Test signals are correct drawing in normal/highlighted states, menu opening/closing redraws, and Kerberos indicator rendering when aklog is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.m

## Purpose
Implements the custom drawing and menu interaction for the OpenAFS backgrounder status item.

## Important APIs, Types, And Functions
Methods include `initWithFrame:backgrounder:menu:`, `drawRect:`, `makeKerberosIndicator:`, `mouseDown:`, `menuWillOpen:`, `menuDidClose:`, and `menuNeedsUpdate:`. It uses `drawStatusBarBackgroundInRect:withHighlight:`, `imageToRender`, `compositeToPoint:operation:`, `NSAttributedString`, `NSFont`, and `popUpStatusItemMenu:`.

## Control Flow
`drawRect:` paints the status bar background, draws the current token-state image, and overlays a small `K` indicator when the delegate reports aklog mode. `mouseDown:` sets itself as menu delegate and opens the menu. Menu callbacks toggle highlight state and forward `menuNeedsUpdate:` to the backgrounder delegate so titles/enabled states are fresh before display.

## State And Persistence
The implementation stores only transient highlight/menu references and has no persistent side effects.

## Dependencies And Integration Points
It is instantiated by `AFSBackgrounderDelegate setStatusItem:` and bridges user clicks into the delegate's `NSMenu`. It depends on image assets and `global.h` constants such as menu-bar height.

## Risks And Test Signals
Risks include deprecated `NSCompositeSourceOver`/`compositeToPoint` APIs, fixed drawing origin/indicator placement, and delegate lifetime assumptions. Test signals include visual state updates after token changes, menu highlight behavior, click-to-open, and no drawing errors when images are nil.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/AFSMenuExtraView.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.h

## Purpose
Declares the controller for the credential-entry nib used by the backgrounder. It captures username/password fields and posts a notification when the user submits or cancels.

## Important APIs, Types, And Functions
The interface declares outlets/ids for the credential view, parent menu controller, username and password text fields, state flag `taken`, and stored `uName`/`uPwd`. Public methods are `getToken:`, `closePanel:`, `takenToken`, `uName`, and `uPwd`.

## Control Flow
The controller is driven by nib actions. Submit records field values, sets `taken`, and notifies the menu controller; cancel clears `taken` and notifies as well.

## State And Persistence
It stores entered credentials in memory as Objective-C strings. Token creation is performed by `AFSMenuCredentialContoller` after reading this state.

## Dependencies And Integration Points
It integrates `CredentialWindow.nib` with `AFSMenuCredentialContoller` and distributed notification constant `kLogWindowClosed`.

## Risks And Test Signals
Risks include untyped outlets, password string retention without wiping, and returning internal string references. Test signals are nib action wiring, submit/cancel notification delivery, and correct values returned to the wrapper controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.m

## Purpose
Implements the credential-entry nib controller. It records submitted username/password values, marks whether token acquisition was requested, and posts a close notification for the surrounding credential window controller.

## Important APIs, Types, And Functions
Methods are `awakeFromNib`, `getToken:`, `closePanel:`, `takenToken`, `uName`, and `uPwd`. It uses `NSTextField stringValue` and `NSDistributedNotificationCenter postNotificationName:kAFSMenuExtraID object:kLogWindowClosed`.

## Control Flow
`getToken:` reads username and password fields, returns early if either is empty according to pointer comparison with `@""`, sets `taken=YES`, and posts the close notification. `closePanel:` sets `taken=NO` and posts the same notification. Accessors return the captured state.

## State And Persistence
State is in-memory only: `taken`, `uName`, and `uPwd`. The actual AFS token side effect happens later in `AFSMenuCredentialContoller`.

## Dependencies And Integration Points
It is loaded from `CredentialWindow.nib` and coordinates with `AFSMenuCredentialContoller` through distributed notifications.

## Risks And Test Signals
Risks include using pointer equality for empty string checks, not copying/retaining field values explicitly, password lifetime/wiping concerns, and no validation feedback. Test signals include submit with empty fields, submit with valid credentials, cancel flow, and notification observer cleanup in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/CredentialWindow/CredentialWindowController.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/main.m -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/main.m

## Purpose
Entry point for the macOS `AFSBackgrounder` Cocoa application.

## Important APIs, Types, And Functions
The file imports Cocoa and defines `main(int argc, char *argv[])`, returning `NSApplicationMain(argc, (const char **)argv)`.

## Control Flow
Process startup immediately hands control to Cocoa's application runtime, which loads the app bundle/nib and invokes `AFSBackgrounderDelegate` through normal application delegate wiring.

## State And Persistence
No state is stored in this file. Runtime application state is owned by Cocoa and the delegate.

## Dependencies And Integration Points
It links the backgrounder executable into the macOS app bundle packaged by the OpenAFS preference pane.

## Risks And Test Signals
Risks are minimal and limited to application bundle/nib configuration. Test signals are successful app launch, delegate initialization, and clean exit code propagation from `NSApplicationMain`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSBackgrounder/main.m -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.h -->
# sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.h

## Purpose
Declares the main OpenAFS macOS preference pane controller. It manages UI for AFS service state, cache parameters, CellServDB entries, tokens, aklog/login preferences, Kerberos renewal, menu/backgrounder activation, startup behavior, and desktop link configuration.

## Important APIs, Types, And Functions
The class subclasses `NSPreferencePane` and implements table data source/delegate protocols. It imports PreferencePanes, SecurityInterface authorization UI, `AFSPropertyManager`, global constants, and link-creation support. It declares private CoreMenuExtra functions for adding/removing menu extras. Ivars include many IBOutlet controls, sheets/controllers, `AFSPropertyManager`, filtered CellServDB data, token list, timer, locks, and link configuration. Methods cover pane lifecycle, authorization, timers, refresh/save actions, AFS start/stop, token/unlog, menu activation, aklog/startup/Kerberos preference changes, CellServDB filtering/editing, token refresh notifications, volume-change notifications, table delegates, and table value providers.

## Control Flow
The implementation (outside this header) uses these actions and outlets to load preferences into the UI, allow authorized edits, persist preference values, notify the backgrounder/menu extra, start/stop AFS via `AFSPropertyManager`, manage token lists, edit CellServDB/link data, and respond to tab/table/timer events.

## State And Persistence
The controller's runtime state includes UI controls, current token/cell/link lists, timers, locks, and sheet controllers. Persistent state flows through CFPreferences, OpenAFS config files under `/var/db/openafs`, launchd/menu-extra settings, and CellServDB/cache configuration managed by `AFSPropertyManager`.

## Dependencies And Integration Points
It is the user-facing preference pane counterpart to the backgrounder. It integrates with privileged authorization, CoreMenuExtra APIs, `AFSPropertyManager`, distributed notifications, launch agents/daemons, and the OpenAFS macOS package resources.

## Risks And Test Signals
Risks include very broad controller responsibility, private CoreMenuExtra API compatibility, many untyped `id` outlets, manual memory/timer management, and preference/backgrounder synchronization drift. Test signals include pane load/unload, authorization lock/unlock, saving cache and preference values, start/stop service actions, CellServDB table edits, token refresh, menu/backgrounder toggle, Kerberos renewal settings, and link configuration persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/AFSCommanderPref.h -->
