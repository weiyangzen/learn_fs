# sources/distributed-fs/ceph/src/rgw/rgw_iam_policy.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header defines the IAM policy data model: action bit indexes, service aggregate masks, `op_to_perm()`, `Environment`, `MaskedIP`, `Condition`, `Statement`, `PolicyParseException`, and `Policy`. Policies parse JSON text into in-memory structures, then evaluate request environment, identity, action bit, and resource ARN. It integrates IAM with legacy S3 ACL permission bits and RGW auth/ARN utilities. Risks include enum order/bit compatibility, contiguous service mask assumptions, loose typed-condition conversions, and principal-type classification. Tests should cover masks, string/action parity, `op_to_perm()`, condition conversions, IP equality, parse exceptions, and policy inspection helpers.
