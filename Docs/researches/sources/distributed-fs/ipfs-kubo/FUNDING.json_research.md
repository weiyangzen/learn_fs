# sources/distributed-fs/ipfs-kubo/FUNDING.json

## Purpose
This metadata file declares an Optimism Retro Funding project identifier for Kubo.

## Important APIs, Types, And Functions
It contains a single `opRetro.projectId` string.

## Control Flow
There is no code flow; consumers parse the JSON metadata.

## State And Persistence Behavior
It is static project funding metadata.

## Dependencies And Integration Points
It integrates with funding/indexing systems that understand the `opRetro` schema.

## Risks And Test Signals
Risks are invalid JSON or an incorrect project ID. Test signals are successful JSON parsing and correct recognition by funding tooling.
