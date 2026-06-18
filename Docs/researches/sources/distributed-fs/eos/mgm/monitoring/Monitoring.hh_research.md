# sources/distributed-fs/eos/mgm/monitoring/Monitoring.hh

Purpose: declares monitoring log helper functions for the MGM Prometheus endpoint.

Important APIs: the header exposes start, started, stopped, start-failed, and configuration-error logging functions in `eos::mgm::monitoring`. Start/start-failed functions carry bind address; start/started also include cache TTL seconds.

Control flow and state behavior: this is a pure declaration header with no state. It gives monitoring code a stable logging API while keeping `common/Logging.hh` out of consumers that only need declarations.

Dependencies and integration points: depends on fixed-width integer and string headers. Implemented by `Monitoring.cc` and used by monitoring endpoint setup code.

Risks and test signals: API stability matters because these helper names encode endpoint lifecycle events. Tests should focus on implementation logging format and ensuring configuration/start failures route to the error helper.
