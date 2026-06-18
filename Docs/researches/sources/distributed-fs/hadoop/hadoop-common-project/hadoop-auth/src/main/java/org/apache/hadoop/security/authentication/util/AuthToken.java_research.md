<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/AuthToken.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/AuthToken.java

## Purpose
Represents the serializable principal data stored inside Hadoop Auth cookies before signing. It carries user name, principal, auth type, expiration, and optional max-inactive timestamp.

## Important APIs, types, and functions
`AuthToken(String userName, String principal, String type)` validates required fields. `setExpires()` updates the expiration and regenerates the serialized token; `setMaxInactives()` stores the inactivity timestamp. `isExpired()` checks both expiration and max-inactive values. `toString()` returns the `u=...&p=...&t=...&i=...&e=...` representation. `parse()` strips surrounding quotes, splits key/value pairs, removes a signature field `s`, validates required attributes, parses timestamps, and creates a token.

## Control flow
Tokens start with unset expiration/inactivity. Serialization is generated when expiration is set or in the protected anonymous constructor. Parsing first tokenizes on `&`, then builds a map and rejects missing required attributes. Optional `i` is processed before `e`, which regenerates the final token string.

## State and persistence
The token is mutable in memory and its string form is persisted externally in signed cookies. Attribute values cannot contain `&`, but are otherwise not escaped, so the serialization format is a simple flat key-value protocol.

## Dependencies and integration points
Implements `Principal`; used by `AuthenticationToken`, `AuthenticationFilter`, `AuthenticatedURL`, and `Signer`. Throws client `AuthenticationException` on malformed token strings.

## Risks and test signals
Risks include no escaping for `=`, duplicate attributes overwriting earlier values, `NumberFormatException` escaping from parse for bad timestamps, `setMaxInactives()` not regenerating until `setExpires()` is called, and clock-skew sensitivity. Tests should cover quoted cookies, missing attributes, duplicate keys, bad numeric values, max-inactive-only transitions, reserved separator rejection, and signature-field stripping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth/src/main/java/org/apache/hadoop/security/authentication/util/AuthToken.java -->
