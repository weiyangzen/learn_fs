## sources/control-plane/csi-driver-smb/charts/artifacthub-repo.yml

Purpose: declares Artifact Hub repository metadata for the SMB CSI Helm chart repository. It stores the repository ID and owner contact.

State is declarative metadata consumed by Artifact Hub indexing. Dependencies are Artifact Hub schema expectations and the maintainer email remaining valid. Risks are low but operational: stale ownership data can break repository claiming or notifications. Test signal is external Artifact Hub repository validation rather than in-repo CI.
