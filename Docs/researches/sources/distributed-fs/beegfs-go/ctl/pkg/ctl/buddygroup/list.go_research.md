# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/buddygroup/list.go

Purpose: retrieves buddy group information from management and converts protobuf data into CTL-friendly result structs.

Important APIs/types/functions: `GetBuddyGroups_Result`; `GetBuddyGroups`.

Control flow: fetches all buddy groups, converts buddy group/primary/secondary IDs from protobuf, maps protobuf node types to BeeGFS node types, formats consistency-state strings, and returns a slice of results.

State and persistence: read-only.

Dependencies and integration points: depends on `config.ManagementClient`, BeeGFS entity conversion helpers, management protobuf API, target/buddy group protobuf fields, and BeeGFS protobuf node type constants.

Risks: conversion errors abort the whole list. Unknown node types must be handled consistently by conversion logic. Consistency states are strings, so downstream consumers should not parse them as stable enums unless documented.

Test signals: no direct tests. Useful tests would use representative protobuf buddy groups for meta and storage, conversion failures, unknown/zero states, and empty response.
