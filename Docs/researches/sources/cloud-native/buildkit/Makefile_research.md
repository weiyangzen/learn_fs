# sources/cloud-native/buildkit/Makefile

## Purpose
Developer and CI convenience wrapper around Docker Buildx Bake and repository scripts. It provides standard targets for binaries, cross builds, images, frontend images, install, release, clean, tests, lint, validations, vendoring, generated files, archutil, authors, doctoc, and docs.

## APIs, Flow, And State
The Makefile resolves `BUILDX_CMD` from `BUILDX_BIN`, `docker buildx`, standalone `buildx`, or defaults to `docker buildx`. Most targets call `$(BUILDX_CMD) bake <target>`. `release` flattens `bin/release`; `vendor` writes a temporary bake output, replaces `./vendor`, and cleans the temp dir; `install` copies `bin/build/*` to `DESTDIR$(bindir)`; `clean` removes `./bin`.

## Dependencies And Integration
Depends on Docker Buildx, bake target names in `docker-bake.hcl`, `hack/test`, shell utilities, and environment variables such as `DESTDIR`, `BUILDX_BIN`, `IMAGE_TARGET`, and `FRONTEND_CHANNEL`.

## Risks And Test Signals
`vendor` is destructive to `./vendor` by design, so interrupted runs can leave a partial vendor tree. `release` assumes a nested output layout. Test signals are target exit codes and artifact/tree changes under `bin`, `vendor`, generated files, docs, and author lists.
