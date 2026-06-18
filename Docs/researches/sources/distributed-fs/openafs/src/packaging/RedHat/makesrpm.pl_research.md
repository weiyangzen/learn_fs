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
