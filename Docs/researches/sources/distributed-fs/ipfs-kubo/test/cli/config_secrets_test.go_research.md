# sources/distributed-fs/ipfs-kubo/test/cli/config_secrets_test.go

Purpose: security regression coverage for config secret redaction and TLS-insecure flags.

Important APIs/functions: `TestConfigSecrets`, `harness.Node.ReadFile`, `ConfigFile`, `RunIPFS`, `WriteBytes`, and `sjson.Set`.

Control flow: private key subtests compare raw config file contents to `ipfs config show`, reject direct `Identity.PrivKey` and `Identity` reads, reject `config replace` attempts that set `PrivKey`, and verify replacing redacted config preserves the existing key. TLS subtests confirm insecure skip-verify fields default non-true and can be explicitly set.

State/persistence: initializes repos, reads and writes config JSON, and relies on offline config replacement preserving secret fields.

Dependencies/integration: config command redaction, config validation/replacement, identity private key storage, and optional config fields `AutoConf.TLSInsecureSkipVerify` and `HTTPRetrieval.TLSInsecureSkipVerify`.

Risks/test signals: high security value. Line-based private-key extraction is simple and assumes pretty JSON formatting with a `PrivKey` line.
