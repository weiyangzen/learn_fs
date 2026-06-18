# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/OAuth2Constants.java

## Purpose

`OAuth2Constants` centralizes string constants for WebHDFS OAuth2 form bodies and JSON fields.

## Important APIs, Types, And Functions

It defines `URLENCODED`, `ACCESS_TOKEN`, `BEARER`, `CLIENT_CREDENTIALS`, `CLIENT_ID`, `CLIENT_SECRET`, `EXPIRES_IN`, `GRANT_TYPE`, `REFRESH_TOKEN`, and `TOKEN_TYPE`. The constructor is private.

## Control Flow

No runtime logic exists beyond class loading constants.

## State And Persistence

Only static final strings exist.

## Dependencies And Integration Points

Used by OAuth token providers and request configurator when building form data and parsing token endpoint responses.

## Risks

Changing any value breaks OAuth protocol interoperability. The `BEARER` constant is not the same as `OAuth2ConnectionConfigurator.HEADER`, so duplicated bearer spelling should remain consistent.

## Test Signals

OAuth provider request-body and response-parse tests indirectly validate these constants.
