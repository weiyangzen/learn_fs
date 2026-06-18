# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/AccessTokenTimer.java

## Purpose

`AccessTokenTimer` tracks OAuth access-token expiry and decides when refresh should occur before actual expiration.

## Important APIs, Types, And Functions

Key members are `EXPIRE_BUFFER_MS`, `Timer`, `nextRefreshMSSinceEpoch`, constructors, `setExpiresIn`, `setExpiresInMSSinceEpoch`, `getNextRefreshMSSinceEpoch`, `shouldRefresh`, and static `convertExpiresIn`.

## Control Flow

OAuth `expires_in` seconds are converted to epoch milliseconds using the injected timer. `shouldRefresh` returns true when current time is later than expiry minus the 30-second buffer.

## State And Persistence

It stores only the next refresh epoch in memory. Configuration-based refresh-token provider can seed this from a configured epoch.

## Dependencies And Integration Points

Used by credential and refresh-token OAuth providers. It depends on Hadoop `Timer` for testable time.

## Risks

Bad numeric strings throw unchecked parse exceptions. Very short expiry values refresh immediately. Clock skew and wall-clock jumps can affect behavior.

## Test Signals

Tests should use fake timers for before-buffer, inside-buffer, expired, zero/default, and configured epoch cases.
