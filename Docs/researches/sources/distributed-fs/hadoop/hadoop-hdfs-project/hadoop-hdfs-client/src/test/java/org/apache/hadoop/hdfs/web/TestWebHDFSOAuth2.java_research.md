## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/TestWebHDFSOAuth2.java

Purpose: this integration-style test verifies that WebHDFS OAuth2 support obtains an access token and sends it as an authorization header on a WebHDFS `listStatus` call.

Important APIs and types: it uses `WebHdfsFileSystem`, `ConfCredentialBasedAccessTokenProvider`, `CredentialBasedAccessTokenProvider.OAUTH_CREDENTIAL_KEY`, OAuth config keys, `OAuth2ConnectionConfigurator.HEADER`, MockServer `ClientAndServer`, `MockServerClient`, and JSON `FileStatus` response parsing.

Control flow: `BeforeEach` starts separate MockServer instances for OAuth and WebHDFS. The OAuth server expects a POST to `/refresh` with client credentials form data and returns JSON containing `access_token`, `expires_in`, and token type. The WebHDFS mock expects a GET to `/webhdfs/v1/test1/test2` with the bearer header and returns two file statuses. The test initializes a `WebHdfsFileSystem`, calls `listStatus()`, verifies both expected requests, and checks parsed names.

State and persistence: state is confined to mock server expectations, OAuth config, the filesystem instance, and JSON response bodies. Servers bind fixed ports and are stopped in `AfterEach`.

Dependencies and integration points: integrates WebHDFS filesystem initialization, OAuth2 token provider configuration, HTTP request decoration, MockServer matching, Jackson JSON generation, and WebHDFS JSON-to-`FileStatus` conversion.

Risks: fixed ports 7552/7553 can collide on shared test hosts. Request body matching assumes exact form encoding/order used by the provider.

Test signals: confirms OAuth refresh is performed once, WebHDFS calls include the authorization header, and token-enabled `listStatus()` parses the returned file list.
