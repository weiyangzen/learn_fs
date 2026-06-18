# sources/cloud-native/moby/daemon/logger/loggerutils/logfile_test.go

Purpose: broad unit tests for shared `LogFile`.

Important APIs/types/functions: tests cover write/read, tailing, rotation, compression, close behavior, decode errors, and reader cancellation paths using test decoders/tail readers.

Control flow/state/persistence: creates temporary log files and rotated generations, writes serialized test entries, and consumes watchers.

Dependencies/integration: validates shared behavior relied on by json-file and local drivers.

Risks: fake codecs may differ from production JSON/protobuf details, so driver tests complement this file.

Test signals: high-value coverage for persistence and rotation edge cases.
