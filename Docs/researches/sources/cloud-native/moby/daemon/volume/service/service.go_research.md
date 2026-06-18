# sources/cloud-native/moby/daemon/volume/service/service.go

## Purpose
High-level volume API service used by daemon handlers, wrapping `VolumeStore`, driver listing, event logging, API conversion, prune, and live restore.

## Important APIs, Types, And Functions
`VolumesService` contains `VolumeStore`, driver lister, prune-running flag, and event logger. Methods include `NewVolumeService`, `GetDriverList`, `Create`, `Get`, `Mount`, `Unmount`, `Release`, `Remove`, `LocalVolumesSize`, `Prune`, `List`, `Shutdown`, and `LiveRestoreVolume`. `AnonymousLabel` marks generated anonymous volumes.

## Control Flow
Startup creates a driver store, registers default local driver, and creates a metadata-backed store. `Create` generates anonymous IDs and labels when name is empty, delegates to store, and converts to API type. `Get` optionally resolves driver status. `Mount`/`Unmount` look up by API volume name/driver and call underlying volume. `Remove` maps not-found/in-use to API-friendly behavior. `Prune` serializes concurrent prunes with an atomic flag, normalizes filters, finds unreferenced local volumes without options, computes reclaim size, removes each, and emits a prune event. `List` converts filtered volumes using cached paths.

## State And Persistence
Service mutates store metadata and driver volume state through delegated calls. `pruneRunning` is in-memory concurrency state.

## Dependencies And Integration Points
Integrates API volume types/events, filters, directory sizing, driver store/plugin getter, local driver setup, idtools, and error mapping.

## Risks
Prune intentionally skips non-local and option-backed local volumes. Size calculation before remove can race with filesystem changes. Event logger is assumed non-nil in prune paths. API conversion may use cached mountpoints for list.

## Test Signals
Service tests cover create conflicts, list filters, remove purge, get status/driver conflicts, prune filters, and local volume size.
