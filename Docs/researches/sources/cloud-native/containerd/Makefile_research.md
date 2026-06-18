# sources/cloud-native/containerd/Makefile

## Purpose
The Makefile is containerd's main build, test, generation, release, install, and cleanup entry point.

## Important APIs, Types, And Functions
It defines build variables (`GO`, `ROOTDIR`, `PREFIX`, `VERSION`, `REVISION`, `PACKAGE`, `GOOS`, `GOARCH`, tags, ldflags), packages (`PACKAGES`, `API_PACKAGES`, root-test package discovery), binaries (`ctr`, `containerd`, `containerd-stress`), manpages, release names, and many phony targets.

Major targets include `all`, `check`, `ci`, `generate`, `protos`, `check-protos`, `proto-fmt`, `build`, `test`, `root-test`, `integration`, `cri-integration`, failpoint helper binaries, `benchmark`, `binaries`, `man`, `install-man`, `install-doc`, `release`, `static-release`, `install-cri-deps`, deprecated CRI release targets, `clean`, `clean-test`, `install`, `uninstall`, `coverage`, `root-coverage`, `cri-integration-coverage`, `vendor`, `verify-vendor`, `clean-vendor`, and `help`.

## Control Flow
Default `all` builds binaries. Build targets use Go package lists and ldflags embedding version metadata. Proto generation updates Buf deps, runs generation, removes undesired generated files, fixes acronyms, applies build tags, and may add a module replace if `api/next.txtpb` changed. Test targets separate normal, root, integration, and CRI integration flows. Release targets package binaries and checksums. Vendor verification copies the repo to a temporary directory, runs tidy/vendor/verify, and diffs back.

## State And Persistence
The Makefile creates `bin/`, `man/`, `releases/`, `_output/`, coverage files, generated proto files, vendor changes, installed files under `DESTDIR/PREFIX`, and may remove runtime test debris in `clean-test`.

## Dependencies And Integration Points
It integrates with Go, Buf, custom generators (`go-buildtag`, `protoc-gen-go-fieldpath`), setup/test scripts, CI workflows, release Dockerfile, devcontainer setup, systemd unit packaging, CNI/runc/cri-tools installers, and platform-specific `Makefile.$(GOOS)`.

## Risks
Targets like `clean-test` kill processes and unmount test leftovers, so they require care. Package discovery shells out to Go and git; missing tools change behavior. Generated proto and vendor targets can modify tracked files. Release/install targets differ by GOOS, especially Windows CRI deps.

## Test Signals
Important validations are `make check`, `make binaries`, `make test`, `make root-test`, `make integration`, `make cri-integration`, `make verify-vendor`, `make check-protos`, release Dockerfile builds, and CI matrix success.
