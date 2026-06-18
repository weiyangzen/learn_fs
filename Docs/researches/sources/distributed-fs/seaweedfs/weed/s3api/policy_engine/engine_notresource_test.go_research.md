# sources/distributed-fs/seaweedfs/weed/s3api/policy_engine/engine_notresource_test.go

Purpose: focused regression test for `NotResource` statements that contain policy variables.

Important APIs and functions: `TestNotResourceWithVariables` installs a policy with `AllowOwnFolder` on `Resource` and `DenyOtherFolders` on `NotResource`, both using `${aws:username}`.

Control flow: first evaluation substitutes Alice into the allow and deny patterns. Alice's own object matches the allow and also matches the `NotResource` pattern, which means the deny statement does not apply. The second evaluation targets Bob's folder, so it does not match the allow and does satisfy the deny `NotResource` condition.

State and persistence: all policy state is in memory.

Dependencies and integration: directly validates `CompiledStatement.DynamicNotResourcePatterns`, `PolicyEngine.matchesDynamicPatterns`, and deny precedence in `engine.go`.

Risks: this test covers only one action and one variable. Unsupported conditions or missing variable context could still change real policy behavior.

Test signals: gives a narrow, high-value safety signal for dynamic `NotResource`, which is easy to regress when optimizing compiled statement matching.
