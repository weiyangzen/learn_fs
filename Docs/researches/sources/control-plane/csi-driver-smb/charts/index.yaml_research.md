## sources/control-plane/csi-driver-smb/charts/index.yaml

Purpose: is the Helm repository index for packaged SMB CSI charts. It maps chart name `csi-driver-smb` to historical versions, package URLs in the GitHub raw chart tree, digests, app versions, and created timestamps.

Important behavior is declarative: Helm clients use `apiVersion: v1`, `entries`, and `generated` to resolve chart packages. The index includes current 1.x releases, older v0.x releases, and two `v0.0.0`/latest entries pointing at latest or v1.9.0 packages.

State is persisted release metadata and SHA digests. Dependencies are Helm repo index format and package files matching URLs/digests. Risks include duplicate version semantics around `v0.0.0`, mixed `v`-prefixed and unprefixed versions in newer releases, stale raw GitHub URLs, and digest mismatch after package regeneration. Test signal is `helm repo update/search/install` behavior.
