# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authorize/TestDefaultImpersonationProvider.java

Purpose: tests `DefaultImpersonationProvider` handling of proxy-user names that contain dots or spaces, especially successful wildcard authorization and failure messaging for space-containing proxy users.

Important APIs and types: `DefaultImpersonationProvider`, `ProxyUsers.CONF_HADOOP_PROXYUSER`, `UserGroupInformation`, `Configuration`, Mockito mocks, `AuthorizationException`, and `LambdaTestUtils.intercept`.

Control flow: setup creates a provider with proxy entries for `fakeuser`, `test.user`, and `test user2`, all with wildcard groups/hosts, then initializes using the standard proxy-user prefix. Success tests mock a proxy UGI with real users `fakeuser` and `test.user` and authorize from `2.2.2.2`. Failure test uses real user `test user2`, proxied user `dummyUser`, and asserts the authorization exception includes `User: test user2 is not allowed to impersonate dummyUser`.

State and persistence: in-memory configuration/provider only; mocks are nulled after each test.

Dependencies and integration points: integrates proxy-user configuration parsing and `UserGroupInformation.getRealUser`/short-name APIs.

Risks: tests are narrow and use mocks, so they do not validate actual group membership or host list matching. Behavior for spaces is partly a negative case despite wildcard-like setup, reflecting parsing/normalization sensitivity.

Test signals: useful regression signal for proxy user key parsing with special characters and error text from default impersonation authorization.
