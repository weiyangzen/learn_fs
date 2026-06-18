## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestClientCredentialTimeBasedTokenRefresher.java

Purpose: this test verifies client-credentials OAuth2 refresh behavior for `ConfCredentialBasedAccessTokenProvider`.

Important APIs and types: it builds `Configuration` with credential, `ACCESS_TOKEN_PROVIDER_KEY`, `OAUTH_CLIENT_ID_KEY`, and `OAUTH_REFRESH_URL_KEY`; uses `AccessTokenProvider.getAccessToken()`, `Timer`, MockServer, `ParameterBody`, and OAuth2 constants such as `client_secret`, `grant_type=client_credentials`, and `access_token`.

Control flow: the test selects an available port, configures the token as expired, starts MockServer, expects a POST to `/refresh` with ordered form parameters, returns JSON token metadata, then asserts `getAccessToken()` returns the new token and verifies the expected request occurred exactly once.

State and persistence: state is test configuration, mocked time, MockServer expectation/response, and provider's cached access token/expiry. No durable state is written.

Dependencies and integration points: integrates the OAuth2 provider config contract, OkHttp/form parameter generation, Jackson JSON response generation, and MockServer request verification.

Risks: request body matching is order-sensitive because OkHttp does not sort parameters; the test compensates with `ParameterBody.params`. Server cleanup is manual and must run to free the chosen port.

Test signals: confirms expired client-credential providers POST the correct grant request to the configured refresh URL and parse the returned access token.
