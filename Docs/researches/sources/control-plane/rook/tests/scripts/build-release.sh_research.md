<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/build-release.sh -->
# sources/control-plane/rook/tests/scripts/build-release.sh

Purpose: release CI helper for building Rook, publishing images/docs, and promoting Helm charts for tagged releases.

Important APIs and control flow: it loads `.env`, rewrites `DOCS_GIT_REPO` to token-auth HTTPS when `GIT_API_TOKEN` exists, determines whether the run is master, release branch, or tag, resolves tag branch provenance with `git branch -r --contain`, runs `make build.all` and `make mod.check`, then invokes `make -C build/release build` and `publish`. `publish_charts` runs only for tagged releases.

State, persistence, and integration: writes build artifacts, pushes images/docs/charts, and may expose git status/diff in background. Dependencies include GNU make, git, AWS credentials, GitHub token, and Rook release make targets. Risks include exporting `.env` through `xargs`, backgrounded git diagnostics racing with output, and destructive publish side effects if environment variables are wrong. Test signals are make target success and optional chart promotion completion.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/build-release.sh -->
