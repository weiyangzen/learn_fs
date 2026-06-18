# sources/distributed-fs/eos/mgm/misc/IdTrackerWithValidity.hh

Purpose: template utility for tracking IDs temporarily claimed by MGM subsystems such as balancing, conversion, draining, and fsck. It prevents duplicate work on the same entry across tracker types while automatically expiring claims after a validity period.

Important APIs and types: `TrackerType` enumerates `None`, `All`, `Balance`, `Convert`, `Drain`, and `Fsck`. `IdTrackerWithValidity<EntryT>` is constructed with cleanup interval, default entry validity, and optional fake clock. Public methods are `AddEntry`, `HasEntry`, `RemoveEntry`, `DoCleanup`, `Clear`, `GetClock`, `TrackerTypeToString`, `StringToTrackerType`, and `PrintStats`. Internally it stores `std::map<TrackerType, std::map<EntryT, time_point>>` under a mutex.

Control flow: `AddEntry` rejects invalid aggregate tracker types (`None` and `All`), scans all tracker maps to enforce global uniqueness, then records an expiry timestamp using either caller-supplied validity or the default. `DoCleanup` runs only after `mCleanupTimestamp` passes, advances the next cleanup timestamp, and removes expired entries for all trackers or one selected tracker. `RemoveEntry` erases the first matching entry from any tracker. `PrintStats` emits either human or monitoring-style lines and can include the full tracked ID list.

State and persistence behavior: all state is in memory and intentionally temporary. The optional `SteadyClock` wrapper supports deterministic unit tests. Clearing `TrackerType::All` removes every tracker map; clearing a specific tracker leaves other subsystem claims intact.

Dependencies and integration points: depends on EOS namespace macros, `common/SteadyClock`, mutexes, and maps. The global MGM file-id tracker is stored on `XrdMgmOfs` as `mFidTracker` and used by balancer, converter, drain, stripes, admin space commands, and admin namespace tracker reporting.

Risks and test signals: cleanup is gated by one global cleanup timestamp, so calling `DoCleanup` for one tracker can postpone cleanup for other trackers until the next interval. `PrintStats(full=true)` assumes `EntryT` is streamable. `AddEntry` scans all maps, so very large tracker sets have linear cross-tracker insertion cost. Tests in `unit_tests/mgm/IdTrackerTests.cc` cover basic add, fake-clock cleanup, custom validity, removal, and clear behavior. Additional tests should cover cross-tracker duplicate rejection, tracker string conversion for unknown values, monitor formatting, and cleanup interaction across different tracker types.
