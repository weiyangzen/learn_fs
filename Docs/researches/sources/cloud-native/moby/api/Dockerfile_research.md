<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/Dockerfile -->
# sources/cloud-native/moby/api/Dockerfile

## Purpose
Defines a small API-module development image for swagger generation and validation.

## Important APIs, Types, And Functions
- Uses `golang:${GO_VERSION}-alpine` as `base`.
- Installs `bash`, `make`, and `yamllint`.
- `swagger` stage installs `github.com/go-swagger/go-swagger/cmd/swagger@v0.33.1` with BuildKit caches.
- `dev` stage copies the swagger binary and sets workdir `/go/src/github.com/moby/moby/api`.

## Control Flow
The API Makefile builds the `dev` target. During image build, the swagger stage compiles the pinned swagger CLI and verifies it with `swagger version`; the final dev stage makes that binary available to scripts.

## State And Persistence
Go build and module caches can persist through BuildKit cache mounts. Final image state contains the swagger binary and Alpine tooling.

## Dependencies And Integration Points
Used by `api/Makefile` targets `swagger-gen`, `validate-swagger`, and `validate-swagger-gen`, and indirectly by top-level `test.yml` API swagger validation.

## Risks And Edge Cases
The Makefile passes `SWAGGER_VERSION`, while this Dockerfile declares `GO_SWAGGER_VERSION`; the default still works, but override naming must be handled carefully. Alpine tooling can differ from Debian dev image behavior.

## Test Signals
Image build success and `swagger version` output are build-time signals; script success in API Makefile targets validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/Dockerfile -->
