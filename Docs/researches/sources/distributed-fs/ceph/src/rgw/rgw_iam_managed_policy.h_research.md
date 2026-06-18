# sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header declares `get_managed_policy()` and the serializable `ManagedPolicies` container, a Boost flat set of attached managed policy ARNs. Callers persist ARNs and resolve to concrete `Policy` objects at evaluation time. It integrates with IAM metadata and Ceph `bufferlist` encoding. Risks include behavior changing when embedded managed policies change and duplicate attachments being silently coalesced by the set. Tests should cover duplicate suppression, empty and multi-ARN encode/decode, lookup integration, and unsupported stored ARN handling.
