## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/test/java/org/apache/hadoop/hdfs/web/oauth2/TestAccessTokenTimer.java

Purpose: this test validates `AccessTokenTimer`, the small OAuth2 helper that converts token expiry values into a next-refresh timestamp and decides whether a token should be refreshed.

Important APIs and types: it uses `AccessTokenTimer`, injectable Hadoop `Timer`, `setExpiresIn()`, `setExpiresInMSSinceEpoch()`, `getNextRefreshMSSinceEpoch()`, and `shouldRefresh()`.

Control flow: one test fixes timer `now()` at 5 ms, sets `expires_in` to 3 seconds, and verifies the next refresh timestamp is 3005 ms and already considered refreshable under the timer policy. The second sets an absolute expiry and uses sequential mocked `now()` values to verify false before expiry and true at/after expiry.

State and persistence: state is only the timer's stored next-refresh epoch and mocked current time. No persistence exists.

Dependencies and integration points: supports OAuth2 access token providers that need to avoid unnecessary refresh calls while refreshing after expiry.

Risks: exact millisecond arithmetic is part of the contract; policy changes such as refresh skew would require updating tests.

Test signals: confirms seconds-to-milliseconds conversion, absolute epoch handling, and `Timer.now()`-based refresh decisions.
