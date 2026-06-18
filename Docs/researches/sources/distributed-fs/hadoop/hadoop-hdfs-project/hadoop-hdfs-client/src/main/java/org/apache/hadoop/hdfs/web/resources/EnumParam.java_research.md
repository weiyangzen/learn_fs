# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/web/resources/EnumParam.java

## Purpose

`EnumParam` is the package-private base for single-enum WebHDFS query parameters.

## Important APIs, Types, And Functions

It extends `Param<E, EnumParam.Domain<E>>`. Nested `Domain` stores the enum class, reports valid constants via `getDomain`, and parses strings with uppercase normalization.

## Control Flow

Subclasses provide a domain and enum value. Parsing calls `Enum.valueOf(enumClass, StringUtils.toUpperCase(str))`, so accepted strings are case-insensitive for ASCII enum names.

## State And Persistence

State is inherited parameter value plus the enum class in each domain.

## Dependencies And Integration Points

Used by WebHDFS resource params representing single enum values, while `CreateFlagParam` uses the related enum-set base.

## Risks

Null strings will fail in uppercase/valueOf paths. Enum renames or server/client enum mismatch break compatibility.

## Test Signals

Tests should cover lowercase/mixed-case parsing, invalid values, domain string output, and representative subclass serialization.
