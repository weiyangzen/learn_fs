# Research: sources/distributed-fs/ipfs-kubo/config/config.go

Purpose: Defines the root `Config` schema and core utilities for config path resolution, marshaling, map conversion, reflection-based shape inspection, cloning, and key validation.

Important APIs/types/functions: `Config` aggregates identity, datastore, addresses, routing, gateway, API, swarm, AutoConf, Provide, Import, internal settings, and more. Constants define default path names and `IPFS_PATH`. Functions include `PathRoot`, `Path`, `Filename`, `HumanOutput`, `Marshal`, `FromMap`, `ToMap`, `ReflectToMap`, `(*Config).Clone`, and `CheckKey`/validation helpers later in the file.

Control flow, state, and persistence: Path helpers resolve repo config locations without touching disk. JSON encode/decode is used for typed map conversion and deep-ish cloning. `ReflectToMap` recursively includes exported fields, including fields omitted by JSON, and adds `"*"` samples for maps so config-key validation can handle dynamic keys. Config persistence is handled elsewhere by `config/serialize`.

Dependencies and integration points: Central schema consumed by fsrepo, daemon, commands, profiles, and node construction. Uses `fsutil.ExpandHome`, JSON, reflection, and filepath utilities.

Risks and test signals: Reflection-based key validation can drift from JSON tags or special custom marshalers. `Clone` depends on JSON serialization and can lose unexported/custom runtime-only data. `config_test.go` covers clone isolation, reflected map shape, and important valid/invalid key paths.
