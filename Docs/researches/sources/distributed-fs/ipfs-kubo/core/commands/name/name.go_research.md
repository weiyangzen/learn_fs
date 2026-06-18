# sources/distributed-fs/ipfs-kubo/core/commands/name/name.go

## Purpose

`name/name.go` defines the `ipfs name` command group and implements experimental IPNS record inspection, raw record retrieval, and raw pre-signed record storage. It is the command surface for both high-level IPNS operations and lower-level record debugging/import workflows.

## Important APIs, Types, and Functions

`NameCmd` registers `publish`, `resolve`, `pubsub`, `inspect`, `get`, and `put`. Shared output `IpnsEntry` is used by publish/put. Inspection types are `IpnsInspectValidation`, `IpnsInspectEntry`, and `IpnsInspectResult`. `IpnsInspectCmd` unmarshals and displays IPNS protobuf/DAG-CBOR fields. `IpnsGetCmd` reads raw records through `api.Routing().Get`. `IpnsPutCmd` validates and writes pre-signed raw records through `api.Routing().Put`.

## Control Flow

`inspect` reads a record file/stdin, unmarshals it as an IPNS record, best-effort extracts value, validity type/time, sequence, and TTL, then separately unmarshals protobuf to determine V1/V2 signature style and protobuf size. With `--verify`, it parses the supplied name and calls `ipns.ValidateWithName`; with `--dump`, it includes a hex dump. `get` normalizes a bare name to `/ipns/<name>`, retrieves raw routing bytes, and emits octet-stream content type `application/vnd.ipfs.ipns-record`. `put` validates mutually exclusive offline/delegated flags, optionally checks delegated publisher config, parses the target IPNS name, reads up to 1 MiB from input, and unless `--force` enforces the 10 KiB IPNS spec limit, protobuf validity, signature against name, and increasing sequence relative to any existing record. It then stores the original bytes with `Routing.AllowOffline(allowOffline || allowDelegated)` and emits the name plus extracted value.

## State and Persistence Behavior

`inspect` and `get` are read-only. `put` writes to the routing system and may store locally, broadcast over DHT, or use delegated publishers depending on routing configuration and flags. It does not sign records; it preserves the supplied bytes exactly.

## Dependencies and Integration Points

Dependencies include Boxo `ipns`, IPNS protobuf, CoreAPI routing, Kubo node/config access, protobuf utilities, datastore/routing behavior, and command file handling. It integrates with `name publish`, `routing get/put`, delegated publisher configuration, and IPNS specs.

## Risks and Test Signals

Risks include destructive or invalid records accepted with `--force`, sequence race conditions between validation and put, exact error-string matching for offline failures, memory limits that read only 1 MiB but only spec-check 10 KiB when not forced, and delegated mode relying on config presence. Tests should cover inspect malformed/partial records, verify valid/invalid names, content type for get, put size/signature/sequence checks, identical republish, force behavior, offline/delegated flag combinations, missing delegated publishers, and quiet text output.
