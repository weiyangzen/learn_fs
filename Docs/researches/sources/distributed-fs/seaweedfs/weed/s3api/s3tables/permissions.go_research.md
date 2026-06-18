## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/permissions.go

Purpose: implements S3 Tables resource-policy evaluation, identity action shortcuts, condition matching, and authorization error construction.

Important APIs/types: `PolicyDocument`, custom `UnmarshalJSON`, `Statement`, `PolicyContext`, `CheckPermissionWithContext`, `checkPermission`, `hasIdentityPermission`, `hasAdminAction`, `matchesPrincipal`, `matchesAction`, `matchesActionPattern`, `matchesConditions`, `getConditionContextValues`, `matchesResource`, and `AuthError`.

Control flow: authorization rejects empty principal/owner, allows account admin and owner, then checks static identity actions. If no resource policy exists, `DefaultAllow` decides fallback. Otherwise it parses AWS-style statements, requires principal/action/resource/condition matches, records explicit allow, and lets explicit deny win immediately. Condition evaluation delegates operators to `policy_engine`.

State and persistence: stateless over policy JSON and `PolicyContext`. Dependencies include SeaweedFS policy engine, wildcard matching, glog, and S3 constants.

Risks: invalid policy JSON silently denies; default allow can still permit unmatched statements after policy evaluation; condition context maps only selected S3 Tables and AWS tag keys. Tests cover wildcard matching, AWS principal forms, condition operators, and default-allow/deny precedence.
