# sources/distributed-fs/eos/mgm/devices/Devices.hh

## Purpose
Declares the `Devices` service responsible for periodic device health extraction and proc namespace persistence.

## Important APIs and Types
- `Devices`, `Start`, `Stop`, and `SetDevicesPath` form the lifecycle/configuration API.
- `json_map_t`, `space_map_t`, and `smart_map_t` are shared-pointer map aliases keyed by fsid.
- Getters return current maps and extraction time.
- `Extract` is public, allowing on-demand refresh outside the background recorder.
- Private `Recorder`, `Store`, and map setters implement the background path.

## Control Flow and State
The header shows a single `AssistedThread`, device path string, mutex-protected shared maps, and atomic extraction timestamp. Getters return shared pointers under lock; callers receive a snapshot pointer, not a deep copy.

## Dependencies and Integration Points
Depends on MGM namespace, assisted threading, timing, and XRootD string types. Implementation integrates with `FsView` and namespace services.

## Risks
- The comment says "storing regulary" and there are minor typos, but the main concern is lifecycle: destructor always calls `Stop`.
- Returning shared pointers to maps means readers can mutate map contents unless they treat them as read-only; no const alias is used.
- `lastExtraction` is not initialized in the constructor.

## Test Signals
Tests should validate getter/setter thread safety, initial extraction time behavior, public `Extract` without started recorder, and immutability expectations for returned maps.
