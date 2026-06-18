# sources/distributed-fs/ceph/src/rgw/rgw_iam_managed_policy.cc

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This file embeds supported AWS managed policy JSON for IAM, SNS, and S3 full/read-only access, resolves exact managed-policy ARNs to parsed `rgw::IAM::Policy` objects, and encodes/decodes `ManagedPolicies::arns`. Persistent state is only the attached ARN set; policy documents are static source data. It depends on the IAM policy parser and Ceph buffer encoding. Risks include unsupported AWS managed policies returning empty optional, embedded policy drift, and parse failures after policy parser changes. Tests should cover every supported ARN, unsupported ARNs, policy evaluation, and encode/decode round trips.
