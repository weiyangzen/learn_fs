# sources/cloud-native/moby/daemon/internal/builder-next/exporter/mobyexporter/writer.go

## Purpose
Builds and patches OCI image configuration JSON for images exported into Moby's image store.

## APIs, Control Flow, and Integration
`emptyImageConfig` creates a minimal default-platform config with `WorkingDir`, default PATH, and `rootfs.type=layers`. `parseHistoryFromConfig` extracts history. `patchImageConfig` unmarshals config into raw JSON fields, replaces `rootfs` and `history`, fills `created` from the latest history timestamp when absent, and embeds inline cache under `moby.buildkit.cache.v0`. `normalizeLayersAndHistory` reconciles diffIDs, history entries, and BuildKit ref layer metadata, marking excess history layers empty and filling missing `Created` values. `getRefMetadata` reads description and created time from `cache.ImmutableRef.LayerChain`.

## State, Dependencies, and Risks
State is JSON-only, but it defines persisted image config semantics. Risks include silently rewriting invalid configs into usable-but-surprising history, nil ref metadata defaulting to empty entries, and embedded inline cache increasing config size. Tests assert patching accepts empty/history/rootfs configs and rejects `null`.
