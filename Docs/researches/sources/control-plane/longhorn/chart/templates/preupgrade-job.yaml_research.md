# sources/control-plane/longhorn/chart/templates/preupgrade-job.yaml

Purpose: conditionally runs Longhorn's pre-upgrade checker as a Helm pre-upgrade hook before chart upgrade proceeds.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, Helm `pre-upgrade` hook annotations, `.Values.preUpgradeChecker.jobEnabled`, `.Values.preUpgradeChecker.upgradeVersionCheck`, manager command `pre-upgrade`, privileged security context, hostPath mount `/proc`, `LONGHORN_DISTRO`, `POD_NAMESPACE`, image pull secrets, service account, tolerations, and node selectors.

Control flow: the template renders only when both pre-upgrade checker flags are true. Helm creates the hook before upgrade; the pod runs `longhorn-manager pre-upgrade`, mounts host `/proc`, restarts on failure, and has a 900 second active deadline with one retry.

State and persistence: the job is temporary, but it reads live cluster/host state and can prevent unsafe upgrade progression. It does not persist chart-managed objects beyond hook lifecycle.

Dependencies/integration: depends on manager image compatibility with the old cluster, RBAC from `longhorn-service-account`, host `/proc` access, and Longhorn Manager's pre-upgrade checks. The value comments note GitOps tools may need this disabled.

Risks: privileged host `/proc` access broadens security requirements. GitOps controllers that cannot handle blocking Helm hooks may fail unless the job is disabled. Disabling the job also disables a safety check that Longhorn recommends keeping enabled.

Test signals: render enabled and disabled combinations, run upgrades across supported versions, confirm the hook fails on intentionally unsafe preconditions, and verify Argo CD/GitOps flows when `jobEnabled` is false.
