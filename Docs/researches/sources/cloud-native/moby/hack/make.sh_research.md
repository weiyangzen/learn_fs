# sources/cloud-native/moby/hack/make.sh

## Purpose
Main bundle dispatcher for building Moby binaries and test artifacts inside the project build environment.

## Important APIs and Types
Exports `DOCKER_PKG`, `SCRIPTDIR`, `MAKEDIR`, `PKG_CONFIG`, computes `VERSION`, `GITCOMMIT`, build tags, static ldflags, and defines `bundle()` plus `main()`.

## Control Flow, State, and Persistence
The script normalizes CI ref names into versions, computes build time from `SOURCE_DATE_EPOCH`, resolves git commit and dirty suffix, optionally enters auto-GOPATH mode, adds journald tags when libsystemd is available, sets debug flags, and dispatches requested bundle scripts from `hack/make`. With no args it runs default bundles: daemon binary, dynamic binary, integration tests, and docker-py tests.

## Dependencies, Integration Points, Risks, and Test Signals
All `hack/make/*` scripts depend on its exported environment. It writes bundle artifacts under `bundles/` through child scripts. Risks include environment-sensitive reproducibility, shell word splitting in bundle args, dirty tree version suffixes, and platform-specific linker tags. CI build/test jobs and install scripts are the validation surface.
