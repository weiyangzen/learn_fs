# sources/cloud-native/moby/client/volume_prune.go

## Purpose
Implements pruning unused Docker volumes and decoding reclaimed-space results.

## APIs, Types, And Functions
`VolumePruneOptions` contains `Filters`; `VolumePruneResult` embeds `volume.PruneReport`; `Client.VolumePrune` posts to `/volumes/prune`. It uses errdefs to preserve daemon error classes around unsupported or failed prune operations.

## Control Flow, State, And Integration
The method applies filters to query values, sends `POST /volumes/prune`, decodes the prune report, and closes the reader. Successful calls delete persistent daemon volume data that is not referenced.

## Risks And Test Signals
Risks are destructive behavior through wrong filters, error class loss, and decode issues for deleted-volume lists or space reclaimed. Integration is with daemon volume reference tracking and CLI cleanup commands.
