# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/Security.proto

## Purpose
`Security.proto` defines stable protobuf records for Hadoop tokens, credentials, and delegation-token RPC payloads. It is shared by security-sensitive protocols that need to serialize token identifiers, passwords, kinds, services, and credential collections.

## Important APIs, types, and functions
Messages include `TokenProto`, `CredentialsKVProto`, `CredentialsProto`, `GetDelegationTokenRequestProto`, `GetDelegationTokenResponseProto`, `RenewDelegationTokenRequestProto`, `RenewDelegationTokenResponseProto`, `CancelDelegationTokenRequestProto`, and `CancelDelegationTokenResponseProto`. `TokenProto` requires identifier, password, kind, and service. Credential entries bind an alias to either a token or secret bytes.

## Control flow
Services serialize tokens and credentials for transfer or persistence. Delegation-token protocols use request/response messages to issue, renew, or cancel tokens, with success responses containing a token, new expiry time, or void marker.

## State and persistence
The schema can carry persisted credential material and live delegation-token state. Sensitive fields include token passwords and secret bytes, so transport/storage protections are external but critical.

## Dependencies and integration points
It generates `org.apache.hadoop.security.proto.SecurityProtos` and integrates with Hadoop `Token`, `Credentials`, delegation token secret managers, and multiple filesystem/service protocols.

## Risks and test signals
Risks include secret leakage through logs, compatibility issues around required token fields, ambiguous `CredentialsKVProto` entries containing both token and secret, and unsigned expiry interpretation. Test signals include token/credential round-trip tests, delegation token issue/renew/cancel tests, secure transport tests, and backward compatibility checks for serialized credentials.
