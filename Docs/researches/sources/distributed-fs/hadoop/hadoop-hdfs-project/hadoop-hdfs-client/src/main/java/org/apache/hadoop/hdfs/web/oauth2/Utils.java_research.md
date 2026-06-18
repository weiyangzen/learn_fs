# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/oauth2/Utils.java

## Purpose

`Utils` provides small package-private helpers for WebHDFS OAuth2 configuration and form encoding.

## Important APIs, Types, And Functions

Functions are `notNull(Configuration, String)` and `postBody(String... kv)`.

## Control Flow

`notNull` fetches a configuration value and throws `IllegalArgumentException` if absent. `postBody` requires an even number of key/value arguments, URL-encodes each using UTF-8, and joins them as `application/x-www-form-urlencoded` pairs.

## State And Persistence

No state exists.

## Dependencies And Integration Points

Used by OAuth providers/configurator for required config validation. `postBody` is available but current token providers use Apache `UrlEncodedFormEntity` instead.

## Risks

`notNull` treats empty strings as valid. `postBody` throws checked `UnsupportedEncodingException` even though UTF-8 should always exist on Java platforms.

## Test Signals

Tests should cover missing config, present empty values if policy matters, odd key/value arrays, special-character encoding, and pair ordering.
