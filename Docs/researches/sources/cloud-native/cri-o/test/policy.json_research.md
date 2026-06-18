<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy.json -->
# sources/cloud-native/cri-o/test/policy.json

Purpose: unrestrictive image policy fixture with targeted exceptions for CRI-O image policy tests.

Important structure: `default` accepts anything. The `docker-daemon` transport rejects `quay.io/crio/hello-world` and requires Red Hat GPG signatures for `registry.access.redhat.com` using embedded public key data. This lets tests cover both successful permissive pulls and transport-specific denial/signature paths.

State and integration: consumed by containers/image policy evaluation through CRI-O or test helpers. No runtime state is stored. Risks include the large embedded key material becoming stale or malformed and transport mismatch: entries under `docker-daemon` will not affect `docker://` pulls. Test signal is fixture-based; correctness is proven by higher-level pull/signature tests rather than a parser test here.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/policy.json -->
