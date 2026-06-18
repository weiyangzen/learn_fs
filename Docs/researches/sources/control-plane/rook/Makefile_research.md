# sources/control-plane/rook/Makefile

## Purpose

Top-level build, test, lint, generation, docs, and cleanup entrypoint for the Rook repository.

## Important APIs, Types, and Functions

Important variables include tool versions for controller-gen, chart-testing, kustomize, markdownlint, shellcheck, yamllint image SHA, `GOBIN`, build flags, `TAGS=ceph_preview`, platform lists, package lists, `GO_PROJECT`, and linker version injection. Targets include `build.common`, `build`, `build.all`, `install`, `test`, `test-integration`, `lint.*`, `codegen`, `mod.check`, `clean`, `crds.*`, `gen-rbac`, `docs`, `docs-build`, `generate`, and `help`.

## Control Flow

The Makefile includes shared makelib files, normalizes locale and shell behavior, configures Go build/test variables, and composes high-level targets from lower-level makelib targets. Build paths generate version files, Helm deps, module checks, CRD manifests, RBAC, Go init/validation, binaries, and images. Lint and generation targets call pinned local tools and scripts.

## State and Persistence Behavior

It writes build output under `$(OUTPUT_DIR)`, working/cache directories, generated CRDs/docs/RBAC/code, temporary Helm/kustomize files, and image build artifacts. `clean`, `distclean`, and `prune` remove build/cache/image state.

## Dependencies and Integration Points

It integrates with `build/makelib/common.mk`, `helm.mk`, `golang.mk`, scripts under `build/`, Helm charts, images, Go modules, docs tooling, CI workflows, and validation scripts.

## Risks and Edge Cases

Many CI workflows rely on target names and generated-output determinism. `build.all` only supports cross-platform image build on amd64 hosts. Tool versions embedded here can break CI if updated without corresponding generated file refreshes.

## Test Signals

CI workflows exercise `make codegen`, `make crds`, `make gen-rbac`, `make lint.*`, `make mod.check`, `make test`, `make docs-build`, and Helm/chart targets. Passing workflows validate most key Makefile paths.
