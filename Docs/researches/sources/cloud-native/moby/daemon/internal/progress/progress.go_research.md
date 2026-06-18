<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progress.go -->
# sources/cloud-native/moby/daemon/internal/progress/progress.go

Purpose: defines daemon progress messages and output abstractions for transfers and other long-running operations.

Important APIs and types: `Progress`, `Output`, `ChanOutput`, `DiscardOutput`, `Update`, `Updatef`, `Message`, `Messagef`, and `Aux`.

Control flow: channel output writes progress to a channel and recovers from panics, preserving historical behavior around closed channels. Convenience helpers construct action, message, or auxiliary progress records.

State and persistence: progress records are transient. Channel output writes to caller-owned channel.

Dependencies and integration: used by image pull/push/load/save and similar daemon operations.

Risks: `chanOutput.WriteProgress` suppresses panics and always returns nil, so closed channels can drop progress silently. `Aux` payload is untyped.

Test signals: progress reader tests cover progress emission via channel output indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/progress/progress.go -->
