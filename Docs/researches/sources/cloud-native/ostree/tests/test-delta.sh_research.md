# sources/cloud-native/ostree/tests/test-delta.sh

Purpose: broad static delta CLI integration test covering generation, listing, indexes, bsdiff options, endian handling, pulling, offline apply, deletion, empty deltas, summaries, rebases, and error handling.

Important APIs/functions: `static-delta generate/list/reindex/indexes/show/delete/apply-offline`, `pull-local --require-static-deltas`, `--disable-static-deltas`, `--commit-metadata-only`, `summary -u`, `core.no-deltas-in-summary`, and helper delta directory lookup.

Control flow: creates binary commits, generates empty and from-to deltas, checks idempotent generation, tests inline vs detached parts and bsdiff knobs, validates show output and endian heuristics using fixtures, pulls via deltas including commitpartial, applies offline, deletes deltas, handles empty delta parts, toggles summary index publication, tests rebase deltas, and rejects bad delta names.

State/persistence: heavily mutates `repo/deltas`, summaries, temp repos, fixture repos, and content refs. Dependencies include user xattrs and pre-endian tar fixtures.

Integration/risk/test signals: protects the static delta subsystem end to end. Risks are output regex brittleness, fixture size assumptions, and compression variability. Fourteen TAP cases provide milestone signals.
