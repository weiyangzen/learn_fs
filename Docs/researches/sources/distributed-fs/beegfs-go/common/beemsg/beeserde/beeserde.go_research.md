# sources/distributed-fs/beegfs-go/common/beemsg/beeserde/beeserde.go

## Purpose
`beeserde.go` implements BeeGFS BeeSerde serialization and deserialization primitives used by BeeMsg protocol messages. It serializes integers, raw bytes, C strings, sequences, string sequences, maps, padding, and matching deserialization operations.

## APIs and Control Flow
`Serializer` owns a bytes buffer, message feature flags, and sticky error. `NewSerializer`, `Finish`, `Fail`, and helpers write little-endian integers, byte slices, length-prefixed null-terminated C strings with optional alignment, sequences/maps with placeholder counts/sizes, string sequences with total size and null terminators, and zero padding. `Deserializer` mirrors this with a buffer, message feature flags, sticky error, `Finish` that requires full consumption, and helpers for integers, bytes, C strings, sequence lengths, sequences, string sequences, maps, and skip.

## State, Persistence, and Dependencies
State is in-memory serialization buffers and feature flags. The wire format is persistent protocol state shared with BeeGFS C++/Rust implementations, so exact byte compatibility is critical. Dependencies include `bytes`, `encoding/binary`, `fmt`, and `reflect`.

## Risks and Test Signals
`SerializeMap` iterates Go maps in randomized order, which can produce nondeterministic wire bytes if protocol peers expect ordering. `DeserializeBytes` uses `Read`, which can return short reads without error for some readers; `bytes.Buffer` usually behaves predictably but `io.ReadFull` semantics would be stricter. `DeserializeInt` calls `reflect.ValueOf(into).Type()` and can panic on nil interface. Tests cover ints, CStr alignment, string seq null rejection, nested sequences/maps, and non-pointer integer deserialization.
