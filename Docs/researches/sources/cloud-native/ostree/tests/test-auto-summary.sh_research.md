# sources/cloud-native/ostree/tests/test-auto-summary.sh

Purpose: tests automatic summary update configuration for commits and ref mutations.

Important APIs/functions: `setup_test_repository "bare"`, `$OSTREE commit`, `summary --update`, `config set core.commit-update-summary`, `config set core.auto-update-summary`, `reset`, `refs --delete`, and md5 comparisons.

Control flow: creates a summary, confirms ordinary commits do not update it, enables `commit-update-summary` and confirms commit changes it, verifies manual summary update deletes `summary.sig`, then tests `auto-update-summary` for adding, changing, and deleting refs.

State/persistence: mutates `repo/summary`, `repo/summary.sig`, branch refs, and repo config. Dependencies are deterministic summary file changes.

Integration/risk/test signals: protects repository metadata freshness knobs. Risks include MD5 comparison sensitivity to unrelated summary metadata and system clock changes. Four TAP plan entries are emitted.
