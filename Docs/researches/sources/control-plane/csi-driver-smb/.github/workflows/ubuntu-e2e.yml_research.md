## sources/control-plane/csi-driver-smb/.github/workflows/ubuntu-e2e.yml

Purpose: defines an Ubuntu e2e workflow for SMB CSI, but the job is explicitly disabled with `if: false`.

If enabled, it would setup Go `^1.16`, checkout, run `make deploy-kind`, build the default target, and run `make e2e-test`. State would include a kind cluster and e2e deployment resources, but none are created while disabled.

Dependencies are dormant: kind deployment utilities, Makefile e2e target, and cluster-capable GitHub runners. Risks are mostly coverage-related: Ubuntu e2e tests do not currently protect pull requests, so Linux runtime integration issues depend on other CI or external systems. Test signal is intentionally absent until the job is re-enabled.
