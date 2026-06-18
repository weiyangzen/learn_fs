## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestRefreshTokenTimeBasedTokenRefresher.java

Purpose: this test verifies refresh-token OAuth2 behavior for `ConfRefreshTokenBasedAccessTokenProvider`.

Important APIs and types: it configures `OAUTH_REFRESH_TOKEN_KEY`, `OAUTH_REFRESH_TOKEN_EXPIRES_KEY`, `OAUTH_CLIENT_ID_KEY`, and `OAUTH_REFRESH_URL_KEY`; uses `AccessTokenProvider`, `Timer`, MockServer form matching, and OAuth2 constants for `grant_type=refresh_token`, `refresh_token`, `client_id`, `token_type=bearer`, and `access_token`.

Control flow: with mocked current time past the configured expiry, the provider calls the refresh endpoint. MockServer expects a POST with client id, grant type, and refresh token parameters, returns JSON token metadata, and the assertion checks the provider returns the new access token.

State and persistence: runtime state is the configuration, provider cache, mocked time, and mock HTTP server expectation. No files are persisted.

Dependencies and integration points: validates the refresh-token provider's HTTP form contract and JSON parsing path used by WebHDFS OAuth2 clients.

Risks: the test uses fixed port 7552, which can collide. Parameter ordering and exact body matching are part of the expected behavior.

Test signals: confirms expired refresh-token credentials trigger exactly one correctly formed refresh request and the response access token is exposed to callers.
