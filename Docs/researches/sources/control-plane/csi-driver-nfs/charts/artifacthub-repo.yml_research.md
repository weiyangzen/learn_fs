# sources/control-plane/csi-driver-nfs/charts/artifacthub-repo.yml

Purpose: declares Artifact Hub repository ownership metadata for the NFS CSI driver Helm chart repository.

Important APIs and types: contains `repositoryID` and one owner entry with name and email.

Control flow: Artifact Hub reads this metadata when indexing or verifying chart ownership.

State and persistence: declarative repository metadata only.

Dependencies and integration: integrates with Artifact Hub chart listing and ownership workflows.

Risks: stale owner contact can break chart maintenance or verification notices.

Test signals: Artifact Hub repository page ownership/status.
