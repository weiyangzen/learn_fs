## sources/cloud-native/moby/daemon/logger/gelf/gelf_test.go

Purpose: Linux tests for GELF address parsing, option validation, writer creation, and driver construction.

Important tests: `TestParseAddress` requires protocol and TCP/UDP schemes. `TestTCPValidateLogOpt` accepts TCP basics and reconnect options, rejects compression on TCP, negative/non-integer reconnect values, and TCP-only options on UDP. `TestUDPValidateLogOpt` accepts UDP compression and common tag/label/env options, rejects invalid compression level/type, unknown options, and missing address. `TestNewGELFTCPWriter` creates a local TCP listener and verifies writer setup/close. `TestNewGELFUDPWriter`, `TestNewTCP`, and `TestNewUDP` validate construction and close paths.

Control flow and state: TCP tests bind port 0 to avoid fixed-port conflicts and use the listener address in config. UDP tests use `127.0.0.1:0`.

Dependencies and integration points: Exercises `Graylog2/go-gelf` writers and logger `Info` option handling. The file is Linux-build-tagged, likely because SCTP/network stack or external writer behavior differs elsewhere.

Risks covered: Protects user-facing validation for protocol-specific options and basic endpoint construction. It does not assert actual GELF message payload content from `Log`.
