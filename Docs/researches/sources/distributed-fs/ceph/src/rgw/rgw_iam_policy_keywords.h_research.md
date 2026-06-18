# sources/distributed-fs/ceph/src/rgw/rgw_iam_policy_keywords.h

See the grouped research section in `Docs/researches/groups/subset-b-006989_research.md` for the complete report.

This header defines IAM parser token categories and ids: top-level and statement keys, condition operators, dynamic condition keys, versions, effects, and principal types. The generated keyword hash and parser state machine use `TokenKind`/`TokenID` to validate context and populate parsed policy fields. It is compile-time metadata with no runtime persistence beyond parsed enum values. Risks are synchronization failures when adding operators or grammar tokens across keyword generation, parser switches, condition evaluation, and printing. Tests should parse every token, verify invalid contexts, and exercise each version/effect/operator.
