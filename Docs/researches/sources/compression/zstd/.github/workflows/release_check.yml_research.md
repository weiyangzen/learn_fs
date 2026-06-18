# sources/compression/zstd/.github/workflows/release_check.yml

Purpose: release-branch guard ensuring generated documentation is committed before release.

Important behavior: on pushes and pull requests to `release`, `verify-manual` saves `doc/zstd_manual.html`, runs `make manual`, and fails if the regenerated file differs. `verify-man-pages` installs Ruby and `ronn`, saves `programs/zstd.1`, `zstdgrep.1`, and `zstdless.1`, runs `make -C programs man`, and fails if any regenerated man page differs.

State, dependencies, and integration: temporary `.saved` files are created in the checkout. It integrates `contrib/gen_html`, the top-level manual target, `programs` man generation, and Ruby gem tooling.

Risks and test signals: the workflow depends on deterministic generator output and current `ronn` behavior. It is a strong release hygiene signal, but it does not validate archive packaging or binaries; those are separate release workflows.
