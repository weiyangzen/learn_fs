<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/stripsecrets/stripsecrets.go -->
## sources/control-plane/ceph-csi/internal/util/stripsecrets/stripsecrets.go

Purpose: redacts Ceph secret material from command argument slices before logging.

APIs and control flow: `InArgs(args)` copies the input slice, attempts to redact the first `--key=` or `--keyfile=` argument, and only if no key/keyfile is found attempts to redact the first `secret=` option. `stripSecret` uses `strings.Cut` to preserve prefix and suffix around comma-separated option values.

State and persistence: stateless; input slice is left unchanged.

Dependencies: standard `strings`.

Integration points: intended for logging command arguments that may include Ceph credentials in explicit key flags or mount option strings.

Risks: intentionally handles only one occurrence and prioritizes key/keyfile over `secret=`, so multiple secrets can remain if present. `stripSecret` suffix reconstruction is index-sensitive and should be tested for options before/after `secret=`.

Test signals: no test file listed in this subset, so behavior is inferred from implementation comments.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/stripsecrets/stripsecrets.go -->
