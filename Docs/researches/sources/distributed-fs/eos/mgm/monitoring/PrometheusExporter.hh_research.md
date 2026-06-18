# sources/distributed-fs/eos/mgm/monitoring/PrometheusExporter.hh

## Purpose
`PrometheusExporter.hh` declares the small owning wrapper that exposes MGM metrics through Prometheus. It hides prometheus-cpp implementation details from `XrdMgmOfs` while tying the endpoint to the traffic-shaping engine, cluster label, scrape cache TTL, and master-only collection predicate.

## Important APIs, Types, And Functions
The class `eos::mgm::monitoring::PrometheusExporter` has one constructor:
`PrometheusExporter(std::string bind_address, traffic_shaping::TrafficShapingEngine& engine, std::string cluster, std::chrono::milliseconds cache_ttl, std::function<bool()> should_collect)`.
It has a destructor, deleted copy constructor, and deleted copy assignment. Private state is `mCollectors`, retaining registered `prometheus::Collectable` objects, and `mExposer`, the HTTP exposer.

## Control Flow
The header defines the ownership contract only. Construction starts the endpoint and registers collectors in the `.cc`; destruction tears down the exposer through RAII. Copying is disabled because the exposer binds a listening endpoint and the collector registrations should have a single owner.

## State And Persistence Behavior
The wrapper owns runtime-only endpoint state. It persists no configuration to disk and does not own the referenced `TrafficShapingEngine`; the engine must outlive the exporter instance.

## Dependencies And Integration Points
It forward-declares prometheus-cpp classes and includes `mgm/shaping/TrafficShaping.hh` for the engine type. `XrdMgmOfs` stores the exporter in a `std::unique_ptr`, recreating it when monitoring configuration changes and resetting it during shutdown.

## Risks And Edge Cases
Lifetime coupling is important: the engine reference and master predicate capture must remain valid while scrapes are possible. Bind-address conflicts and exposer construction failures surface from the implementation constructor. Since the class is non-copyable but movable operations are not declared, callers should treat it as unique-owner only.

## Test Signals
Compile tests should verify the header can be included without pulling in prometheus definitions. Runtime tests should construct and destroy an exporter with a test engine, verify copy operations are rejected at compile time, and exercise failure handling through the `XrdMgmOfs::ApplyMonitoringConfig()` integration path.
